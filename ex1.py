import streamlit as st
import plotly.express as px
import pandas as pd

# Data Load and Cleanup
udash = pd.read_csv('university_student_dashboard_data.csv')
udash.columns = (udash.columns.str.replace(r'[^\w\s]', '', regex=True)
                         .str.strip()
                         .str.replace(r' ', '_', regex=True))
udash['Retention_Rate'] = udash['Retention_Rate']/100
udash['Student_Satisfaction'] = udash['Student_Satisfaction']/100

#Logo
st.image("SUNY-Poly-horizontal-logo.png", width=250)

# Title
st.title("Student Admissions Dashboard")

# Sidebar Filter
year_options = sorted(udash['Year'].unique())
term_options = sorted(udash['Term'].unique())

selected_year = st.sidebar.selectbox("Select Year", ["All"] + year_options)
selected_term = st.sidebar.selectbox("Select Term", ["All"] + term_options)

# KPIs
st.header("Key Indicators")

udash_kpi = udash.copy()
if selected_year != "All":
    udash_kpi = udash_kpi[udash_kpi['Year'] == selected_year]
    header_year = f"{selected_year}"
else:
    udash_kpi = udash
    header_year = "All Years"

# Group by Term
for term, group in udash_kpi.groupby("Term"):
    st.header(f"{term} {header_year}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Applications", f"{group['Applications'].sum():,}")
    col2.metric("Total Admitted", f"{group['Admitted'].sum():,}")
    col3.metric("Total Enrolled", f"{group['Enrolled'].sum():,}")

# Enrollment KPIs
st.header("Student Enrollment")

col1, col2 = st.columns((2))

if selected_year != "All":
    # Only include rows where Year is less than or equal to the selected year
    enrollment_data = udash[udash['Year'] <= selected_year]
else:
    enrollment_data = udash.copy()

# Group by Year and sum up the enrollments
enrollment_yoy = enrollment_data.groupby('Year', as_index=False)['Enrolled'].sum()

with col1: 
# Create the bar chart
    fig_enrollment = px.bar(
        enrollment_yoy,
        x='Year',
        y='Enrolled',
        title="Student Enrollment Year-over-Year",
        labels={"Enrolled": "Total Enrolled"}
    )
    fig_enrollment.update_xaxes(tickmode='linear', dtick=1)
    st.plotly_chart(fig_enrollment, use_container_width=True)

# Enrollment by Department
udash_filtered = udash.copy()

if selected_year != "All":
    udash_filtered = udash_filtered[udash_filtered['Year'] == selected_year]

if selected_term != "All":
    udash_filtered = udash_filtered[udash_filtered['Term'] == selected_term]

# Aggregate Enrollment by Department
total_engineering = udash_filtered['Engineering_Enrolled'].sum()
total_business    = udash_filtered['Business_Enrolled'].sum()
total_arts        = udash_filtered['Arts_Enrolled'].sum()
total_science     = udash_filtered['Science_Enrolled'].sum()

dept_df = pd.DataFrame({
    'Department': ['Engineering', 'Business', 'Arts', 'Science'],
    'Enrolled':   [
        total_engineering,
        total_business,
        total_arts,
        total_science
    ]
})

with col2: 
# Donut Chart of Enrollment by Department
    dept_fig = px.pie(
        dept_df,
        values='Enrolled',
        names='Department',
        title='Enrollment by Department',
        hole=0.4  
    )

    dept_fig.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(dept_fig, use_container_width=True)


# Retention KPIs
st.header("Student Retention")

# Create filtered df for plots
def filter_data(df, year, term):
    """Return a subset of the data based on the chosen year and term."""
    temp = df.copy()
    if year != "All":
        temp = temp[temp['Year'] <= year]  # 'Up to that year'
    if term != "All":
        temp = temp[temp['Term'] == term]
    return temp

def group_by_year(df):
    """Group data by Year, aggregating Retention_Rate and Student_Satisfaction"""
    return df.groupby('Year', as_index=False)[['Retention_Rate', 'Student_Satisfaction']].mean()

def group_by_term(df, term_value):
    """Filter by a specific term, then group by Year"""
    temp = df[df['Term'] == term_value]
    return group_by_year(temp)


# Logic and Plotting by selection
if selected_year == "All" and selected_term == "All":
    st.subheader("All Years, All Terms")

    # Retention & Student Satisfaction YoY (all terms combined)
    df_all = group_by_year(udash)
    fig_all = px.line(
        df_all,
        x='Year',
        y=['Retention_Rate', 'Student_Satisfaction'],
        title="All Terms (Year over Year)",
        labels={
        "Retention_Rate": "Retention Rate",
        "Student_Satisfaction": "Student Satisfaction Rate"
        }
    )
    fig_all.update_yaxes(title_text="Rate (%)")
    st.plotly_chart(fig_all)


    # Fall term YoY
    df_fall = group_by_term(udash, 'Fall')
    fig_fall = px.line(
            df_fall,
            x='Year',
            y=['Retention_Rate', 'Student_Satisfaction'],
            title="Fall Term (Year over Year)",
            labels={"Retention_Rate": "Retention Rate",
            "Student_Satisfaction": "Student Satisfaction Rate"
            }
        )
    fig_fall.update_yaxes(title_text="Rate (%)")
    st.plotly_chart(fig_fall, use_container_width=True)


    # Spring term YoY
    df_spring = group_by_term(udash, 'Spring')
    fig_spring = px.line(
            df_spring,
            x='Year',
            y=['Retention_Rate', 'Student_Satisfaction'],
            title="Spring Term (Year over Year)",
            labels={"Retention_Rate": "Retention Rate",
            "Student_Satisfaction": "Student Satisfaction Rate"
            }
        )
    fig_spring.update_yaxes(title_text="Rate (%)")
    st.plotly_chart(fig_spring, use_container_width=True)

elif selected_year != "All" and selected_term == "All":
    st.subheader(f"Up to Year {selected_year}, All Terms")

    # Filter data up to selected_year
    df_filtered = udash[udash['Year'] <= selected_year]

    # Fall term YOY up to that year (bar chart)
    df_fall = group_by_term(df_filtered, 'Fall')
    fig_fall = px.bar(
            df_fall,
            x='Year',
            y=['Retention_Rate', 'Student_Satisfaction'],
            title=f"Fall Term up to {selected_year}",
            barmode='group',
            labels={"Retention_Rate": "Retention Rate",
            "Student_Satisfaction": "Student Satisfaction Rate"
            }
        )
    fig_fall.update_yaxes(title_text="Rate (%)")
    st.plotly_chart(fig_fall)

    # Spring term YOY up to that year (bar chart)
    df_spring = group_by_term(df_filtered, 'Spring')
    fig_spring = px.bar(
            df_spring,
            x='Year',
            y=['Retention_Rate', 'Student_Satisfaction'],
            title=f"Spring Term up to {selected_year}",
            barmode='group',
            labels={"Retention_Rate": "Retention Rate",
            "Student_Satisfaction": "Student Satisfaction Rate"
            }
        )
    fig_spring.update_yaxes(title_text="Rate (%)")
    st.plotly_chart(fig_spring)

elif selected_year != "All" and selected_term != "All":
    st.subheader(f"Up to Year {selected_year}, {selected_term} Term Only")

    # Filter data up to the selected year AND the specific term
    df_filtered = filter_data(udash, selected_year, selected_term)

    # px.bar for that term YOY up to that year
    df_grouped = group_by_year(df_filtered)
    fig_term = px.bar(
        df_grouped,
        x='Year',
        y=['Retention_Rate', 'Student_Satisfaction'],
        title=f"{selected_term} Term up to Year {selected_year}",
        barmode='group',
        labels={"Retention_Rate": "Retention Rate",
        "Student_Satisfaction": "Student Satisfaction Rate"
        }
    )
    fig_term.update_yaxes(title_text="Rate (%)")
    st.plotly_chart(fig_term)

elif selected_year == "All" and selected_term != "All":
    st.subheader(f"All Years, {selected_term} Term")

    # Only filter by the selected term (all years)
    df_filtered = udash[udash['Term'] == selected_term]

    df_grouped = group_by_year(df_filtered)
    fig_term = px.line(
        df_grouped,
        x='Year',
        y=['Retention_Rate', 'Student_Satisfaction'],
        title=f"{selected_term} Term (All Years)",
        labels={"Retention_Rate": "Retention Rate",
        "Student_Satisfaction": "Student Satisfaction Rate"
        }
    )
    fig_term.update_yaxes(title_text="Rate (%)")
    st.plotly_chart(fig_term)
