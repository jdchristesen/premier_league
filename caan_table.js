var json_file;
var schedule_years = [];

$(document).ready(function(){
     $.when(
        $.getJSON('premier_league_tables.json'),
        $.getJSON('badge_pos.json')
    ).done(function(tables, badge_positions) {
        current_table = tables[0]['2018-2019'];
        caan_table = {};
        max_teams = 0;
        max_points = 0;
        for (i = 0; i < current_table.length; i++){
            points = current_table[i]['points'];
            if (points > max_points){
                max_points = points
            }
            if (!(points in caan_table)){
                caan_table[points] = [];
            }
            caan_table[points][caan_table[points].length] = '.badge-50.' + current_table[i]['badge']
            if (caan_table[points].length > max_teams){
                max_teams = caan_table[points].length;
            }
        }

        console.log(caan_table)
        console.log(max_teams)
        console.log(max_points)

        header = ''
        for (i = 0; i < max_teams; i++){
            header += '<th></th>';
        }

        $('#caan_table tbody tr').append(header);

        for (i = max_points; i > -1; i--){
            new_row = '<tr><td>' + i +'</td>';
//            console.log(caan_table[i.toString()]);
            columns = 0
            if (i.toString() in caan_table){
                teams = caan_table[i.toString()];
                console.log(teams);
                for (j = 0; j < teams.length; j++){
//                    new_row += '<td>' + teams[j] + '</td>';
                    background_pos = badge_positions[0][teams[j]][0] + 'px ' + badge_positions[0][teams[j]][1] + 'px'
                    new_row += '<td><span style="background-image: url(\'images/badges-50-sprite.png\'); background-position: ' + background_pos + '; width:50px;height:50px;display:inline-block;vertical-align:middle"></span></td>'
                    columns += 1
                }
            }
            for (j = 0; j < max_teams - columns; j++){
                new_row += '<td></td>';
            }
            new_row += '</tr>';

            $('#caan_table tbody').append(new_row);

        }

    });
});