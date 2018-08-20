var json_file;
var schedule_years = [];

$(document).ready(function(){

    for (i = 2018; i > 1992; i--){
        var years = i + '-' + (i + 1)
        $('#schedule_year_dropdown').append('<option value=\'' + years + '\'>' + years + '</option>\n');
        $('#' + years).click(function(){ change_schedule_year(); return false; });
    }
    change_schedule_year()
});

function change_schedule_year(){
    var year = $('#schedule_year_dropdown').find(':selected').text();
    var prev_year = $('#schedule_year_dropdown').find(':selected').next().text();
    var months = {'January': '01', 'February': '02', 'March': '03', 'April': '04',
    'May': '05', 'June': '06', 'July': '07', 'August': '08', 'September': '09',
    'October': '10', 'November': '11', 'December': '12'};

    $( "#schedule_table tbody tr:gt(0)" ).each( function(){
        this.parentNode.removeChild( this );
    });

    var matches = {};
    var team_badges = {};

    $.when(
        $.getJSON('results/premier_league_results_' + year + '.json'),
        $.getJSON('results/premier_league_results_' + prev_year + '.json'),
        $.getJSON('premier_league_tables.json')
    ).done(function(current_schedule, prev_schedule, tables) {
        var current_schedule = current_schedule[0];
        var prev_schedule = prev_schedule[0];
        var tables = tables[0];
        var current_teams = [];
        for (i = 0; i < tables[year].length; i++){
            current_teams.push(tables[year][i]['badge']);
        }

        var prev_teams = [];
        for (i = 0; i < tables[prev_year].length; i++){
            var index = current_teams.indexOf(tables[prev_year][i]['badge']);
            if (index != -1){
                current_teams.splice(index, 1);
            } else {
                prev_teams.push(tables[prev_year][i]['badge']);
            }
        }
        current_teams.sort()
        prev_teams.sort()
        var rel_teams = {};
        for (i = 0; i < current_teams.length; i++){
            rel_teams[prev_teams[i]] = current_teams[i]
        }


        for (i = 0; i < current_schedule.length; i++){
            data_date = current_schedule[i]['date'].split(' ');
            if (data_date[1].length == 1){
                data_date = data_date[3] + '/' + months[data_date[2]] + '/0' + data_date[1]
            }else {
                data_date = data_date[3] + '/' + months[data_date[2]] + '/' + data_date[1]
            }

            date = '<td>' + data_date + '</td>';

            home_team = current_schedule[i]['home_team']['team'];
            away_team = current_schedule[i]['away_team']['team'];

            if (home_team == 'Spurs'){
                team = '<td>' + away_team + '</td>';
                badge = current_schedule[i]['away_team']['badge'].split(' ')[1]
                result = current_schedule[i]['home_team']['result'];
                score = current_schedule[i]['home_team']['goals'] + '-' + current_schedule[i]['away_team']['goals'];
            } else if (away_team == 'Spurs'){
                team = '<td>' + home_team + ' (A) </td>';
                badge = current_schedule[i]['home_team']['badge'].split(' ')[1];
                badge += ' (A)'
                result = current_schedule[i]['away_team']['result'];
                score = current_schedule[i]['away_team']['goals'] + '-' + current_schedule[i]['home_team']['goals'];
            } else {
                continue
            }

            if (result == 'W'){
                result = 'win';
                points = 3;
            } else if (result == 'D'){
                result = 'draw';
                points = 1;
            } else if (result == 'L'){
                result = 'loss';
                points = 0;
            } else {
                result = ''
                points = 0;
            }
            if ('score' in current_schedule[i]){
                score = '<td class="' + result + '">' + score +  '</td>';
            } else {
                score = '<td></td>'
            }

            team_badges[badge] = data_date;
            matches[data_date] = {'team': team,
                                  'score': score,
                                  'points': points,
                                  'badge': badge};
        }// end current_schedule for loop

        for (i = 0; i < prev_schedule.length; i++){
            home_team = prev_schedule[i]['home_team']['team'];
            away_team = prev_schedule[i]['away_team']['team'];
            home_badge = prev_schedule[i]['home_team']['badge'].split(' ')[1];
            away_badge = prev_schedule[i]['away_team']['badge'].split(' ')[1];

            if (home_team == 'Spurs'){
                team = '<td>' + away_team + '</td>';
                result = prev_schedule[i]['home_team']['result'];
                score = prev_schedule[i]['home_team']['goals'] + '-' + prev_schedule[i]['away_team']['goals'];
                if (away_badge in rel_teams){
                    badge = rel_teams[away_badge]
                } else {
                    badge = away_badge
                }
            } else if (away_team == 'Spurs'){
                team = '<td>' + home_team + ' (A)</td>';
                result = prev_schedule[i]['away_team']['result'];
                score = prev_schedule[i]['away_team']['goals'] + '-' + prev_schedule[i]['home_team']['goals'];
                if (home_badge in rel_teams){
                    badge = rel_teams[home_badge] + ' (A)'
                } else {
                    badge = home_badge + ' (A)'
                }
            } else {
                continue
            }

            if (result == 'W'){
                result = 'win';
                points = 3;
            } else if (result == 'D'){
                result = 'draw';
                points = 1;
            } else if (result == 'L'){
                result = 'loss';
                points = 0;
            } else {
                result = ''
                points = 0;
            }
            if ('score' in prev_schedule[i]){
                score = '<td class="' + result + '">' + score +  '</td>';
            } else {
                score = '<td></td>'
            }

            if (badge in team_badges){
                matches[team_badges[badge]]['prev_score'] = score;
                matches[team_badges[badge]]['prev_points'] = points;
            }
        }// end prev_schedule for loop

        var keys = Object.keys(matches);
        keys.sort()

        var current_points = 0
        var prev_points = 0
        for (var i = 0; i < keys.length; i++){
            var match = matches[keys[i]];
            new_row = '<tr><td></td>';
            new_row += match['team'];
            new_row += '<td>' + keys[i] + '</td>';
            if ('prev_score' in match){
                new_row += match['prev_score']
            } else {
                new_row += '<td></td>'
            }

            if ('prev_points' in match){
                prev_points += match['prev_points']
            } else {
                prev_points += 0
            }
            new_row += match['score'];
            if (match['score'] != '<td></td>'){
                current_points += match['points']
                new_row += '<td>' + current_points + '</td>';
                new_row += '<td>' + (current_points - prev_points) + '</td>';
                new_row += '<td>' + Math.round((current_points / (i + 1) * keys.length) * 10) / 10 + '</td>';
                new_row += '</tr>';
            } else {
                new_row += '<td></td><td></td><td></td></tr>';
            }

            $('#schedule_table tbody').append(new_row);
        }

        $('#schedule_table tbody tr').each(function(index){
            if (index != 0){
                $(this).find('td:eq(0)').text(index)
            }
        })

        var nodes = [];
        var max_points = 0;

        $("#schedule_table tbody tr:gt(0)").each(function(index){
            var x_loc = Number($(":eq(0)", this).text());
            var y_loc = Number($(":eq(5)", this).text());
            if (y_loc > max_points){
                max_points = y_loc;
            }
            console.log($(":eq(0)", this).text(), $(":eq(5)", this).text());
            console.log(x_loc, y_loc);
            if (!isNaN(x_loc) && !isNaN(y_loc)){
                nodes[index] = {x: Number($(":eq(0)", this).text()),
                                y: Number($(":eq(5)", this).text())};
            }
        });

        c_radius = 5;
        c_diameter = c_radius*2;

        var margin = {top: 20, right: 30, bottom: 30, left: 40},
            width = 900 - margin.left - margin.right,
            height = 600 - margin.top - margin.bottom;
        var x_scale = d3.scale.linear()
            .domain([0, 39])
            .range([0, width]);
        var y_scale = d3.scale.linear()
            .domain([0, max_points + max_points*0.2])
            .range([height - c_diameter, 0]);

        var x_axis = d3.svg.axis()
            .scale(x_scale)
            .orient("bottom");

        var y_axis = d3.svg.axis()
            .scale(y_scale)
            .orient("left");

        var vis = d3.select("#graph")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
        .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        vis.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(x_axis);

        vis.append("g")
            .attr("class", "y axis")
            .call(y_axis)

        vis.selectAll("circle")
           .data(nodes)
           .enter()
           .append("svg:circle")
           .attr("cx", function(d) { return x_scale(d.x); })
           .attr("cy", function(d) { return y_scale(d.y); })
           .attr("r", c_radius.toString() + "px")
           .attr("fill", "steelblue");
    });
}