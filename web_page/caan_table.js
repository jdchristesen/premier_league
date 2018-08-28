var json_file;
var schedule_years = [];

$(document).ready(function(){
      for (i = 2018; i > 1992; i--){
        var years = i + '-' + (i + 1)
        $('#year_dropdown').append('<option value=\'' + years + '\'>' + years + '</option>\n');
        $('#' + years).click(function(){ change_year(); return false; });
    }
    change_year()
});

function change_year(){
    var year = $('#year_dropdown').find(':selected').text();
    var prev_year = $('#year_dropdown').find(':selected').next().text();
    var months = {'January': '01', 'February': '02', 'March': '03', 'April': '04',
    'May': '05', 'June': '06', 'July': '07', 'August': '08', 'September': '09',
    'October': '10', 'November': '11', 'December': '12'};

     $( "#caan_table tbody tr:gt(0)" ).each( function(){
        this.parentNode.removeChild( this );
    });

    $( "#caan_table tbody tr th:gt(0)" ).each( function(){
        this.parentNode.removeChild( this );
    });


    $.when(
        $.getJSON('../premier_league_tables.json')
    ).done(function(tables) {
        current_table = tables[year];
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

        header = ''
        for (i = 0; i < max_teams; i++){
            header += '<th></th>';
        }

        $('#caan_table tbody tr').append(header);

        for (i = max_points; i > -1; i--){
            new_row = '<tr><td>' + i +'</td>';
            columns = 0
            if (i.toString() in caan_table){
                teams = caan_table[i.toString()];
                for (j = 0; j < teams.length; j++){
                    var t = teams[j].split('.')
                    var c = t[1] + ' ' + t[2];
                    new_row += '<td><span class="' + c + '"/></td>';
                    console.log(new_row);
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

}