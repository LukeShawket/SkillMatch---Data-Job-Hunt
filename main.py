import pandas as pd
import streamlit as st
import pdf_picker as rp
import plotly.express as px
import folium
from streamlit_folium import st_folium
import us
import branca
import requests



job_data = "job_data.csv"
job_skills = []
candidate_skills = []
job_matches = {}

df = pd.read_csv(job_data)
all_states = df['state'].tolist()
states = list(set(all_states))


def intro():
    import streamlit as st

    st.write("# SkillMatch\nWelcome to SkillMatch! 👋")
    st.markdown(
        """
        _Job hunting for a data analyst role made me realize how hard it is to find gigs that actually match my skills.
Instead of just dealing with that frustration, I figured—why not build something to make it easier? Plus,
it gave me a chance to learn new stuff along the way. So, I made this._
"""
    )
    st.markdown("""### Getting Started
#### 🔹 **1. Choose a demo**
You can choose a demo in the selection box from the left sidebar
- Home
- JobMatchingTool
- US States Job Distribution
- ...
                
#### 🔹 **2. Job Matching Tool Demo**  
- select your job type 
- Pick your preferred State 
- Upload your resume
- Press Search
- You can checkout the results after you press Search. 

#### 🔹 **3. US States Job Distribution Demo**  
- You can see job information by hovering your mouse on the map or clicking it.

⚠️ **Note:** This is a **demo project** created for **learning purposes only**.    
                Data Source: Job data scraped from LinkedIn at 5/15/2025.""")
    st.sidebar.success("Select a demo above.")

def job_match_demo():
    import streamlit as st

    st.write("# SkillMatch")
    col1, col2 = st.columns(2)
    selected_location = col1.selectbox('Please select a state', sorted(states, key=lambda item: item[1], reverse=True))
    selected_job_type = col1.selectbox('Please select a job type', ('Data Analyst', 'Business Analyst', 'Data Engineer', 'Data Scientist'))
    resume = st.file_uploader("Pick a PDF file", type=["pdf"])

    if resume:
        text = rp.extract_resume(resume)
        result = rp.parse_resume(text)
        
        if st.button('Search'):

            new_df = df[df['job_type'] == selected_job_type]
            filtered_df = new_df[new_df['state'] == selected_location]

            candidate_skills = list(result['skills'])

            
            candidate_skills = [skill.strip().lower() for skill in candidate_skills]

            for index, job in filtered_df.iterrows():

                job_skills = job["required_skills"]
                if isinstance(job_skills, str):
                    job_skills = job_skills.split(", ")

                job_skills = [skill.strip().lower() for skill in job_skills]

                common_skills = set(job_skills) & set(candidate_skills)

                if job_skills[0] != 'unknown':
                    similarity_score = round(len(common_skills)/len(job_skills) * 100, 2)
                    if similarity_score != 0:
                        job_matches[job['id']] = similarity_score
                else:
                    pass
            if len(job_matches) > 0:   
                top_match_jobs = dict(sorted(job_matches.items(), key=lambda item: item[1], reverse=True)[:3])
                match_jobs_df = pd.concat([df[df['id'] == key] for key in top_match_jobs.keys()])
                item = 1
                for index, job in match_jobs_df.iterrows():
                    st.markdown(
                        f"""
#### {item}. {job['title']} - Matching score of {job_matches[job['id']]} %
Title : {job['title']}\n
Company : {job['company']}\n
Location : {job['location']}\n
Salary : {job['salary']}\n
Required Skills : {job['required_skills']}\n
Company Link : [{job['company']}]({job['url']})
"""
                    )
                    item += 1
                with st.expander("Extra Information"):
                    st.write(f"#### All {selected_job_type} jobs in {selected_location}")
                    st.dataframe(filtered_df)
                    st.write("#### Extracted Resume Text")
                    st.markdown(
                        f"""
Name : {result['name']}\n
Email : {result['email']}\n
Phone : {result['phone']}\n
Skills : {", ".join(result['skills'])}\n
Location : {selected_location}\n
Job-Type : {selected_job_type}
"""                 
                    )
            else:
                st.markdown(" ### No jobs that match your skills found!(sad face)")
                with st.expander("Extra Information"):
                    st.write(f"All {selected_job_type} jobs in {selected_location}")
                    st.dataframe(filtered_df)
                    st.write("#### Extracted Resume Text")
                    st.markdown(
                        f"""
Name : {result['name']}\n
Email : {result['email']}\n
Phone : {result['phone']}\n
Skills : {", ".join(result['skills'])}\n
Location : {selected_location}\n
Job-Type : {selected_job_type}
"""                 
                    )



def jobs_states_map():
    import streamlit as st

    state_name_mapping = {abbr: us.states.lookup(abbr).name for abbr in df["state"].unique() if us.states.lookup(abbr)}
    job_count_by_state = {state_name_mapping.get(state, state): count for state, count in df["state"].value_counts().to_dict().items()}
    state_df = pd.DataFrame.from_dict(job_count_by_state, orient="index", columns=["job_count"]).reset_index()

    # Load GeoJSON
    geojson_url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
    geojson_data = requests.get(geojson_url).json()

    # Attach job count data to each state
    for feature in geojson_data["features"]:
        state_name = feature["properties"]["name"]
        feature["properties"]["job_count"] = job_count_by_state.get(state_name, 0)  # Default to 0 if missing

    # Define color scale
    colormap = branca.colormap.LinearColormap(
        vmin=state_df["job_count"].quantile(0.0),
        vmax=state_df["job_count"].quantile(1),
        colors=["red", "orange", "lightblue", "green", "darkgreen"]
    )
    # Create map
    us_map = folium.Map(location=[37.0902, -95.7129], zoom_start=4, tiles=None)

    # Create tooltips and popups
    tooltip = folium.GeoJsonTooltip(fields=["name", "job_count"], aliases=["State:", "Job Count:"], labels=True)
    popup = folium.GeoJsonPopup(fields=["name", "job_count"], aliases=["State", "Job Count"], localize=True)

    # Add GeoJSON layer with job counts
    folium.GeoJson(
        geojson_data,
        style_function=lambda x: {
            "fillColor": colormap(x["properties"]["job_count"]),
            "color": "black",
            "fillOpacity": 0.4,
        },
        tooltip=tooltip,
        popup=popup,
    ).add_to(us_map)

    colormap.add_to(us_map)

    # Display map
    st.write("""## Data Jobs In United States""")
    st_folium(us_map, width=800, height=600)


page_names_to_funcs = {
    "Home": intro,
    "Job Matching Tool": job_match_demo,
    "US States Job Distribution Map": jobs_states_map
}
demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()














