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
    console.log(prev_year)
    var months = {'January': '01', 'February': '02', 'March': '03', 'April': '04',
    'May': '05', 'June': '06', 'July': '07', 'August': '08', 'September': '09',
    'October': '10', 'November': '11', 'December': '12'};

    $( "#schedule_table tbody tr:gt(0)" ).each( function(){
        this.parentNode.removeChild( this );
    });

    var matches = {};
    var team_dates = {};

    $.when(
        $.getJSON('results/premier_league_results_' + year + '.json'),
        $.getJSON('results/premier_league_results_' + prev_year + '.json')
    ).done(function(current_year, prev_year) {
        current_year = current_year[0]
        prev_year = prev_year[0]
        for (i = 0; i < current_year.length; i++){
            data_date = current_year[i]['date'].split(' ');
            if (data_date[1].length == 1){
                data_date = data_date[3] + '/' + months[data_date[2]] + '/0' + data_date[1]
            }else {
                data_date = data_date[3] + '/' + months[data_date[2]] + '/' + data_date[1]
            }

            date = '<td>' + data_date + '</td>';

            home_team = current_year[i]['home_team']['team'];
            away_team = current_year[i]['away_team']['team'];

            if (home_team == 'Spurs'){
                team = '<td>' + away_team + '</td>';
                result = current_year[i]['home_team']['result'];
            } else if (away_team == 'Spurs'){
                team = '<td>' + home_team + ' (A) </td>';
                result = current_year[i]['away_team']['result'];
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
            if ('score' in current_year[i]){
                score = '<td class="' + result + '">' + current_year[i]['score'] +  '</td>';
            } else {
                score = '<td></td>'
            }

            team_dates[team] = data_date;
            matches[data_date] = {'team': team,
                                  'score': score,
                                  'points': points};
        }// end current_year for loop

         for (i = 0; i < prev_year.length; i++){

            home_team = prev_year[i]['home_team']['team'];
            away_team = prev_year[i]['away_team']['team'];

            if (home_team == 'Spurs'){
                team = '<td>' + away_team + '</td>';
                result = prev_year[i]['home_team']['result'];
            } else if (away_team == 'Spurs'){
                team = '<td>' + home_team + ' (A) </td>';
                result = prev_year[i]['away_team']['result'];
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
            if ('score' in prev_year[i]){
                score = '<td class="' + result + '">' + prev_year[i]['score'] +  '</td>';
            } else {
                score = '<td></td>'
            }

            if (team in team_dates){
                console.log(team)
                matches[team_dates[team]]['prev_score'] = score;
                matches[team_dates[team]]['prev_points'] = points;
            }
        }// end prev_year for loop

        var keys = Object.keys(matches);
        keys.sort()

        var current_points = 0
        var prev_points = 0
        for (var i = 0; i < keys.length; i++){
            console.log(keys[i]);
            var match = matches[keys[i]];
            new_row = '<tr><td></td>';
            new_row += match['team'];
            new_row += '<td>' + keys[i] + '</td>';
            if ('prev_score' in match){
                new_row += match['prev_score']
            } else {
                new_row += '<td></td>'
            }
            new_row += match['score'];
            current_points += match['points']
            new_row += '<td>' + current_points + '</td>';
            new_row += '<td>' + current_points + '</td>';
            new_row += '<td>' + current_points / (i + 1) * keys.length + '</td>';
            new_row += '</tr>';
            $('#schedule_table tbody').append(new_row);
        }

        $('#schedule_table tbody tr').each(function(index){
            if (index != 0){
                $(this).find('td:eq(0)').text(index)
            }
        })
    });

}