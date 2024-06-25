graph1='bar';

function initializeChart() {
    // Check if the datatable element exists
    if (document.getElementById('datatable')) {
        console.log('DataTable exists:', document.getElementById('datatable'));
        
        Highcharts.chart('container', {
            data: {
                table: 'datatable'
            },
            chart: {
                type: 'column'
                
            },
            title: {
                text: 'Distribution of issues in the project'
            },
            xAxis: {
                title: {
                    text: 'Issue Type'
                },
                type: 'category'
            },
            yAxis: {
                allowDecimals: false,
                title: {
                    text: 'Amount'
                }
            }
        });
    } else {
        console.error('DataTable element not found.');
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    initializeChart();
    new DataTable('#database');
    
});


function change_graph_type(){
    if(graph1=='bar'){
        graph1='pie';
        var table = document.getElementById('datatable');
        var rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
        var data = [];

        for (var i = 0; i < rows.length; i++) {
            var cells = rows[i].getElementsByTagName('td');
            var type = cells[0].innerText;
            var open = parseFloat(cells[1].innerText);

            data.push({ name: type, y: open });
        }
        Highcharts.chart('container', {
            chart: {
                type: 'pie'
            },
            title: {
                text: 'Distribution of issues in the project'
            },
            tooltip: {
                valueSuffix: '%'
            },
            subtitle: {
                text: 'Source: Issue Data'
            },
            plotOptions: {
                series: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: [{
                        enabled: true,
                        distance: 20
                    }, {
                        enabled: true,
                        distance: -40,
                        format: '{point.percentage:.1f}%',
                        style: {
                            fontSize: '1.2em',
                            textOutline: 'none',
                            opacity: 0.7
                        },
                        filter: {
                            operator: '>',
                            property: 'percentage',
                            value: 10
                        }
                    }]
                }
            },
            series: [{
                name: 'Percentage',
                colorByPoint: true,
                data: data
            }]
        });
    }
    else{
        graph1='bar';
        initializeChart()
    }
    
} 



function showOverview(projectId) {
    fetch(`overview/${projectId}/`)
        .then(response => response.text())
        .then(data => {
            document.getElementById("overview-content").innerHTML = data;
            document.getElementById("measurements-content").innerHTML = ''; // Clear the measurements content
            document.getElementById("admin-content").innerHTML = ''; // Clear the admin content
            initializeChart(); // Initialize the chart after loading content
            new DataTable('#database');

        })
        .catch(error => console.error('Error fetching overview:', error));
  }
  
function showMeasurements(projectId) {
    fetch(`measurements/${projectId}/`)
        .then(response => response.text())
        .then(data => {
            document.getElementById("measurements-content").innerHTML = data;
            document.getElementById("overview-content").innerHTML = ''; // Clear the overview content
            document.getElementById("admin-content").innerHTML = ''; // Clear the admin content
            new DataTable('#result-table-1');
            new DataTable('#result-table-2');
            new DataTable('#result-table-3');
            $('.collapsible-header').on('click', function () {
                var icon = $(this).find('i');
                if ($(this).attr('aria-expanded') === 'true') {
                  icon.removeClass('fa-minus').addClass('fa-plus');
                } else {
                  icon.removeClass('fa-plus').addClass('fa-minus');
                }
              });
            
              $('.collapse').on('show.bs.collapse', function () {
                $(this).prev('.collapsible-header').find('i').removeClass('fa-plus').addClass('fa-minus');
              });
            
              $('.collapse').on('hide.bs.collapse', function () {
                $(this).prev('.collapsible-header').find('i').removeClass('fa-minus').addClass('fa-plus');
              });
            
        })
        .catch(error => console.error('Error fetching measurements:', error));
  }
  
function showAdminEditor() {
    fetch(`AdminEditor/`)
        .then(response => response.text())
        .then(data => {
            document.getElementById("admin-content").innerHTML = data;
            document.getElementById("measurements-content").innerHTML = ''; // Clear the measurements content
            document.getElementById("overview-content").innerHTML = ''; // Clear the overview content
        })
        .catch(error => console.error('Error fetching admin editor:', error));
  }
  
