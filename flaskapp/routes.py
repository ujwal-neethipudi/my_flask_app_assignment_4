from flask import render_template, flash, redirect, url_for, request
from flaskapp import app, db
from flaskapp.models import BlogPost, IpView, Day, UkData
from flaskapp.forms import PostForm
import datetime

import pandas as pd
import json
import plotly
import plotly.express as px


# Route for the home page, which is where the blog posts will be shown
@app.route("/")
@app.route("/home")
def home():
    # Querying all blog posts from the database
    posts = BlogPost.query.all()
    return render_template('home.html', posts=posts)


# Route for the about page
@app.route("/about")
def about():
    return render_template('about.html', title='About page')


# Route to where users add posts (needs to accept get and post requests)
@app.route("/post/new", methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = BlogPost(title=form.title.data, content=form.content.data, user_id=1)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form)


# Route to the dashboard page
@app.route('/dashboard')
def dashboard():
    days = Day.query.all()
    df = pd.DataFrame([{'Date': day.id, 'Page views': day.views} for day in days])

    fig = px.bar(df, x='Date', y='Page views')

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('dashboard.html', title='Page views per day', graphJSON=graphJSON)


@app.before_request
def before_request_func():
    day_id = datetime.date.today()  # get our day_id
    client_ip = request.remote_addr  # get the ip address of where the client request came from

    query = Day.query.filter_by(id=day_id)  # try to get the row associated to the current day
    if query.count() > 0:
        # the current day is already in table, simply increment its views
        current_day = query.first()
        current_day.views += 1
    else:
        # the current day does not exist, it's the first view for the day.
        current_day = Day(id=day_id, views=1)
        db.session.add(current_day)  # insert a new day into the day table

    query = IpView.query.filter_by(ip=client_ip, date_id=day_id)
    if query.count() == 0:  # check if it's the first time a viewer from this ip address is viewing the website
        ip_view = IpView(ip=client_ip, date_id=day_id)
        db.session.add(ip_view)  # insert into the ip_view table

    db.session.commit()  # commit all the changes to the database

@app.route('/check_data')
def check_data():
    # Retrieve all UK data
    uk_data = UkData.query.all()
    
    # Start building the HTML output
    html = "<html><head><title>UK Data Inspection</title>"
    html += "<style>table { border-collapse: collapse; } "
    html += "th, td { border: 1px solid black; padding: 8px; text-align: left; }"
    html += "th { background-color: #f2f2f2; }"
    html += "</style></head><body>"
    
    # Basic stats
    html += f"<h1>UK Data Inspection</h1>"
    html += f"<p>Total records: {len(uk_data)}</p>"
    
    # Show country values
    countries = sorted(set(data.country for data in uk_data if data.country))
    html += f"<h2>Countries in the database ({len(countries)}):</h2>"
    html += "<ul>"
    for country in countries:
        count = sum(1 for data in uk_data if data.country == country)
        html += f"<li>{country} ({count} constituencies)</li>"
    html += "</ul>"
    
    # Sample data table (first 10 records)
    html += "<h2>Sample Data (First 10 Records)</h2>"
    html += "<table><tr><th>ID</th><th>Constituency</th><th>Country</th><th>Turnout19</th><th>ConVote19</th>"
    html += "<th>LabVote19</th><th>TotalVote19</th><th>PopDensity</th></tr>"
    
    for data in uk_data[:10]:
        html += f"<tr>"
        html += f"<td>{data.id}</td>"
        html += f"<td>{data.constituency_name}</td>"
        html += f"<td>{data.country}</td>"
        html += f"<td>{data.Turnout19}</td>"
        html += f"<td>{data.ConVote19}</td>"
        html += f"<td>{data.LabVote19}</td>"
        html += f"<td>{data.TotalVote19}</td>"
        html += f"<td>{data.c11PopulationDensity}</td>"
        html += "</tr>"
    
    html += "</table>"
    
    # Data type information
    sample = uk_data[0] if uk_data else None
    if sample:
        html += "<h2>Data Types</h2><ul>"
        html += f"<li>country: {type(sample.country).__name__}</li>"
        html += f"<li>Turnout19: {type(sample.Turnout19).__name__}</li>"
        html += f"<li>ConVote19: {type(sample.ConVote19).__name__}</li>"
        html += f"<li>TotalVote19: {type(sample.TotalVote19).__name__}</li>"
        html += f"<li>c11PopulationDensity: {type(sample.c11PopulationDensity).__name__}</li>"
        html += "</ul>"
    
    # Check for None or zero values
    if uk_data:
        html += "<h2>Missing or Zero Value Analysis</h2><ul>"
        html += f"<li>Records with None country: {sum(1 for data in uk_data if data.country is None)}</li>"
        html += f"<li>Records with None Turnout19: {sum(1 for data in uk_data if data.Turnout19 is None)}</li>"
        html += f"<li>Records with None ConVote19: {sum(1 for data in uk_data if data.ConVote19 is None)}</li>"
        html += f"<li>Records with None TotalVote19: {sum(1 for data in uk_data if data.TotalVote19 is None)}</li>"
        html += f"<li>Records with None PopDensity: {sum(1 for data in uk_data if data.c11PopulationDensity is None)}</li>"
        
        # Check for zero values in numeric fields
        html += f"<li>Records with zero Turnout19: {sum(1 for data in uk_data if data.Turnout19 == 0)}</li>"
        html += f"<li>Records with zero TotalVote19: {sum(1 for data in uk_data if data.TotalVote19 == 0)}</li>"
        html += f"<li>Records with zero PopDensity: {sum(1 for data in uk_data if data.c11PopulationDensity == 0)}</li>"
        html += "</ul>"
    
    # Check specifically for population density and turnout data
    valid_scatter_data = sum(1 for data in uk_data if data.c11PopulationDensity is not None and data.Turnout19 is not None and data.c11PopulationDensity > 0 and data.Turnout19 > 0)
    html += f"<h3>Records with valid Population Density AND Turnout data: {valid_scatter_data}</h3>"
    
    # Show a few records with complete data for the scatter plot
    complete_records = [data for data in uk_data if data.c11PopulationDensity is not None and data.Turnout19 is not None and data.c11PopulationDensity > 0 and data.Turnout19 > 0]
    if complete_records:
        html += "<h3>Sample Records with Population Density and Turnout (First 5)</h3>"
        html += "<table><tr><th>Constituency</th><th>Country</th><th>PopDensity</th><th>Turnout19</th></tr>"
        
        for data in complete_records[:5]:
            html += f"<tr>"
            html += f"<td>{data.constituency_name}</td>"
            html += f"<td>{data.country}</td>"
            html += f"<td>{data.c11PopulationDensity}</td>"
            html += f"<td>{data.Turnout19}</td>"
            html += "</tr>"
        
        html += "</table>"
    
    html += "</body></html>"
    return html
@app.route('/electoral_analysis')
def electoral_analysis():
    # Fetch all UK data
    uk_data = UkData.query.all()
    
    # Create a dataframe for analysis
    data_list = []
    for data in uk_data:
        # Helper function to safely convert to float
        def safe_float(value):
            if value is None:
                return 0.0  # Replace None with 0
            return float(value)
        
        data_dict = {
            'constituency_name': data.constituency_name,
            'country': data.country,
            'Turnout19': safe_float(data.Turnout19),
            'ConVote19': safe_float(data.ConVote19),
            'LabVote19': safe_float(data.LabVote19),
            'LDVote19': safe_float(data.LDVote19),
            'GreenVote19': safe_float(data.GreenVote19),
            'BrexitVote19': safe_float(data.BrexitVote19),
            'TotalVote19': safe_float(data.TotalVote19),
            'c11PopulationDensity': safe_float(data.c11PopulationDensity)
        }
        data_list.append(data_dict)
    
    uk_df = pd.DataFrame(data_list)
    
    # Calculate vote totals by country
    country_vote_totals = uk_df.groupby('country').agg({
        'ConVote19': 'sum',
        'LabVote19': 'sum',
        'LDVote19': 'sum',
        'GreenVote19': 'sum',
        'BrexitVote19': 'sum',
        'TotalVote19': 'sum'
    }).reset_index()
    
    # Calculate vote percentages
    for party in ['Con', 'Lab', 'LD', 'Green', 'Brexit']:
        vote_col = f"{party}Vote19"
        percent_col = f"{party}VotePercent"
        country_vote_totals[percent_col] = country_vote_totals[vote_col] / country_vote_totals['TotalVote19'] * 100
    
    # Format vote percentage data for display
    party_votes_data = []
    for _, row in country_vote_totals.iterrows():
        party_votes_data.append({
            'Country': row['country'],
            'Conservative': f"{row['ConVotePercent']:.2f}%",
            'Labour': f"{row['LabVotePercent']:.2f}%",
            'Liberal Democrats': f"{row['LDVotePercent']:.2f}%",
            'Green': f"{row['GreenVotePercent']:.2f}%",
            'Brexit': f"{row['BrexitVotePercent']:.2f}%"
        })
    
    # Reshape for visualization (but keep this for consistency even if it doesn't work)
    country_votes_melted = pd.melt(
        country_vote_totals, 
        id_vars=['country'], 
        value_vars=['ConVotePercent', 'LabVotePercent', 'LDVotePercent', 'GreenVotePercent', 'BrexitVotePercent'],
        var_name='Party', 
        value_name='Vote Percentage'
    )
    
    # Clean up party names for display
    party_names = {
        'ConVotePercent': 'Conservative',
        'LabVotePercent': 'Labour',
        'LDVotePercent': 'Liberal Democrats',
        'GreenVotePercent': 'Green',
        'BrexitVotePercent': 'Brexit'
    }
    country_votes_melted['Party'] = country_votes_melted['Party'].map(party_names)
    
    # Create the bar chart
    fig1 = px.bar(
        country_votes_melted,
        x='country',
        y='Vote Percentage',
        color='Party',
        barmode='group',
        title='Party Support by Country (2019)',
        labels={'country': 'Country', 'Vote Percentage': 'Vote Share (%)'},
        category_orders={"country": ["England", "Scotland", "Wales"]}
    )
    
    # For the second visualization, create a summary table
    # Group by country and calculate key statistics
    population_turnout_summary = uk_df.groupby('country').agg({
        'c11PopulationDensity': ['mean', 'min', 'max'],
        'Turnout19': ['mean', 'min', 'max'],
        'constituency_name': 'count'
    }).reset_index()
    
    # Flatten the column hierarchy
    population_turnout_summary.columns = [
        'country' if col[0] == 'country' else 
        f"{col[0]}_{col[1]}" for col in population_turnout_summary.columns
    ]
    
    # Format the summary data for display
    summary_data = []
    for _, row in population_turnout_summary.iterrows():
        summary_data.append({
            'Country': row['country'],
            'Constituencies': int(row['constituency_name_count']),
            'Avg Population Density': f"{row['c11PopulationDensity_mean']:.2f}",
            'Min Population Density': f"{row['c11PopulationDensity_min']:.2f}",
            'Max Population Density': f"{row['c11PopulationDensity_max']:.2f}",
            'Avg Turnout (%)': f"{row['Turnout19_mean']:.2f}",
            'Min Turnout (%)': f"{row['Turnout19_min']:.2f}",
            'Max Turnout (%)': f"{row['Turnout19_max']:.2f}"
        })
    
    # Also get the top 5 constituencies with highest and lowest turnout
    highest_turnout = uk_df.nlargest(5, 'Turnout19')[['constituency_name', 'country', 'Turnout19', 'c11PopulationDensity']]
    lowest_turnout = uk_df.nsmallest(5, 'Turnout19')[['constituency_name', 'country', 'Turnout19', 'c11PopulationDensity']]
    
    # Format these for display
    highest_turnout_data = []
    for _, row in highest_turnout.iterrows():
        highest_turnout_data.append({
            'Constituency': row['constituency_name'],
            'Country': row['country'],
            'Turnout (%)': f"{row['Turnout19']:.2f}",
            'Population Density': f"{row['c11PopulationDensity']:.2f}"
        })
    
    lowest_turnout_data = []
    for _, row in lowest_turnout.iterrows():
        lowest_turnout_data.append({
            'Constituency': row['constituency_name'],
            'Country': row['country'],
            'Turnout (%)': f"{row['Turnout19']:.2f}",
            'Population Density': f"{row['c11PopulationDensity']:.2f}"
        })
    
    # Convert the figure to JSON for rendering
    graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template(
        'electoral_analysis.html',
        title='UK Electoral Analysis (2019)',
        graphJSON1=graphJSON1,
        party_votes_data=party_votes_data,
        summary_data=summary_data,
        highest_turnout_data=highest_turnout_data,
        lowest_turnout_data=lowest_turnout_data
    )
    
@app.route('/check_scatter_data')
def check_scatter_data():
    # Fetch all UK data
    uk_data = UkData.query.all()
    
    # Start building the HTML output
    html = "<html><head><title>Scatter Plot Data Inspection</title>"
    html += "<style>table { border-collapse: collapse; } "
    html += "th, td { border: 1px solid black; padding: 8px; text-align: left; }"
    html += "th { background-color: #f2f2f2; }"
    html += "</style></head><body>"
    
    # Basic stats
    html += f"<h1>Scatter Plot Data Inspection</h1>"
    html += f"<p>Total records: {len(uk_data)}</p>"
    
    # Data type and range inspection for population density and turnout
    pop_densities = [data.c11PopulationDensity for data in uk_data if data.c11PopulationDensity is not None]
    turnouts = [data.Turnout19 for data in uk_data if data.Turnout19 is not None]
    
    html += f"<h2>Population Density Data</h2>"
    html += f"<p>Number of non-None values: {len(pop_densities)} of {len(uk_data)}</p>"
    if pop_densities:
        html += f"<p>Data type: {type(pop_densities[0]).__name__}</p>"
        html += f"<p>Min value: {min(pop_densities)}</p>"
        html += f"<p>Max value: {max(pop_densities)}</p>"
        html += f"<p>Sample values: {pop_densities[:5]}</p>"
    
    html += f"<h2>Turnout Data</h2>"
    html += f"<p>Number of non-None values: {len(turnouts)} of {len(uk_data)}</p>"
    if turnouts:
        html += f"<p>Data type: {type(turnouts[0]).__name__}</p>"
        html += f"<p>Min value: {min(turnouts)}</p>"
        html += f"<p>Max value: {max(turnouts)}</p>"
        html += f"<p>Sample values: {turnouts[:5]}</p>"
    
    # Check for extreme values or anomalies
    html += f"<h2>Data Quality Checks</h2>"
    html += f"<p>Population densities = 0: {sum(1 for d in pop_densities if d == 0)}</p>"
    html += f"<p>Population densities < 0: {sum(1 for d in pop_densities if d < 0)}</p>"
    html += f"<p>Population densities > 10000: {sum(1 for d in pop_densities if d > 10000)}</p>"
    html += f"<p>Turnouts = 0: {sum(1 for t in turnouts if t == 0)}</p>"
    html += f"<p>Turnouts < 0: {sum(1 for t in turnouts if t < 0)}</p>"
    html += f"<p>Turnouts > 100: {sum(1 for t in turnouts if t > 100)}</p>"
    
    # Sample of actual data rows that will be used for the scatter plot
    html += f"<h2>Sample Data Rows for Scatter Plot</h2>"
    html += "<table><tr><th>Constituency</th><th>Country</th><th>PopDensity</th><th>Turnout19</th></tr>"
    
    count = 0
    for data in uk_data:
        if data.c11PopulationDensity is not None and data.Turnout19 is not None:
            html += f"<tr>"
            html += f"<td>{data.constituency_name}</td>"
            html += f"<td>{data.country}</td>"
            html += f"<td>{data.c11PopulationDensity}</td>"
            html += f"<td>{data.Turnout19}</td>"
            html += "</tr>"
            count += 1
            if count >= 20:  # Show first 20 rows
                break
    
    html += "</table>"
    
    # Try to create a very simple test DataFrame and scatter plot
    html += f"<h2>Test Scatter Plot</h2>"
    
    import pandas as pd
    import plotly.express as px
    import json
    import plotly
    
    # Create a tiny test DataFrame with just 5 rows
    test_data = [
        {"x": 1, "y": 10, "category": "A"},
        {"x": 2, "y": 20, "category": "B"},
        {"x": 3, "y": 30, "category": "A"},
        {"x": 4, "y": 40, "category": "B"},
        {"x": 5, "y": 50, "category": "C"}
    ]
    test_df = pd.DataFrame(test_data)
    
    # Try to create a simple scatter plot
    try:
        test_fig = px.scatter(test_df, x='x', y='y', color='category')
        test_json = json.dumps(test_fig, cls=plotly.utils.PlotlyJSONEncoder)
        html += f"<p>Test scatter plot data created successfully.</p>"
        html += f'<div id="test-plot" style="width:600px;height:400px;"></div>'
        html += f'<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>'
        html += f'<script>var test_plot = {test_json}; Plotly.newPlot("test-plot", test_plot.data, test_plot.layout);</script>'
    except Exception as e:
        html += f"<p>Error creating test plot: {str(e)}</p>"
    
    # Try to create a simple scatter plot with actual data
    try:
        real_data = []
        for i, data in enumerate(uk_data):
            if data.c11PopulationDensity is not None and data.Turnout19 is not None:
                real_data.append({
                    "x": float(data.c11PopulationDensity),
                    "y": float(data.Turnout19),
                    "category": data.country
                })
                if i >= 50:  # Just use 50 rows
                    break
        
        real_df = pd.DataFrame(real_data)
        real_fig = px.scatter(real_df, x='x', y='y', color='category')
        real_json = json.dumps(real_fig, cls=plotly.utils.PlotlyJSONEncoder)
        html += f"<p>Real data scatter plot created successfully with {len(real_data)} points.</p>"
        html += f'<div id="real-plot" style="width:600px;height:400px;"></div>'
        html += f'<script>var real_plot = {real_json}; Plotly.newPlot("real-plot", real_plot.data, real_plot.layout);</script>'
    except Exception as e:
        html += f"<p>Error creating real data plot: {str(e)}</p>"
        
    html += "</body></html>"
    return html