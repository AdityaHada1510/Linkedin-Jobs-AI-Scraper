# utils/url_builder.py

def build_linkedin_url(role, location, date_posted, exp_levels, sort_by, job_types, remote_types, easy_apply, under_10):
    date_param_map = {
        "Anytime": "",
        "Past Month": "f_TPR=r2592000",
        "Past Week": "f_TPR=r604800",
        "Past 24 Hours": "f_TPR=r86400"
    }

    exp_map = {"Internship": "1", "Entry Level": "2", "Associate": "3", "Mid-Senior Level": "4"}
    job_type_map = {"Full-time": "F", "Contract": "C", "Volunteer": "V", "Part-time": "P", "Temporary": "T", "Internship": "I"}
    remote_map = {"On-site": "1", "Hybrid": "2", "Remote": "3"}

    base_url = f"https://www.linkedin.com/jobs/search/?keywords={role}&location={location}"

    if date_param_map[date_posted]:
        base_url += f"&{date_param_map[date_posted]}"

    if exp_levels:
        base_url += "&f_E=" + "%2C".join([exp_map[x] for x in exp_levels])

    if job_types:
        base_url += "&f_JT=" + "%2C".join([job_type_map[j] for j in job_types])

    if remote_types:
        base_url += "&f_WT=" + "%2C".join([remote_map[r] for r in remote_types])

    if easy_apply:
        base_url += "&f_AL=true"

    if under_10:
        base_url += "&f_SB2=10"

    base_url += f"&sortBy={'R' if sort_by == 'Most Relevant' else 'DD'}"

    return base_url
