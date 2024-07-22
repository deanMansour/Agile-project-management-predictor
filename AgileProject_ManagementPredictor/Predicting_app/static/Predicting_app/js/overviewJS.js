//Graph type
graph1 = 'bar';

function initializeChart() {
    // Check if the datatable element exists
    if (document.getElementById('datatable')) {

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
    new DataTable('#databaseOver');
    initializeScatterChart();

    // Check for forced colors mode
    if (window.matchMedia && window.matchMedia('(forced-colors: active)').matches) {
        // Handle forced colors mode
        console.log('Forced colors mode active');
    }
});




   

function initializeScatterChart() {
    const table = document.getElementById('datatable2');
    const rows = table.querySelectorAll('tbody tr');

    const issueData = {
        'Critical': [],
        'High': [],
        'Medium': [],
        'Low': [],
        'Not Prioritized': []
    };

    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length === 6) {
            const name = cells[0].innerText.trim();
            const priority = cells[1].innerText.trim() || 'Not Prioritized';
            const created = cells[2].innerText.trim();
            const resolved = cells[3].innerText.trim();
            const estimatedTimeStr = cells[4].innerText.trim(); // Estimated time as string
            const resolutionTimeStr = cells[5].innerText.trim(); // Resolution time as string

            // Convert strings to numbers, handle cases where conversion fails
            const estimatedTime = parseFloat(estimatedTimeStr.replace(/[^0-9.-]/g, ''));
            const resolutionTime = parseFloat(resolutionTimeStr.replace(/[^0-9.-]/g, ''));

            // Validate the numeric values
            if (!isNaN(estimatedTime) && !isNaN(resolutionTime)) {
                const issue = {
                    name: name,
                    x: estimatedTime,
                    y: resolutionTime,
                    created: created,
                    resolved: resolved
                };
              

                if (issueData.hasOwnProperty(priority)) {
                    issueData[priority].push(issue);
                } else {
                    console.error(`Unknown priority: ${priority}`);
                }
            } else {
                console.error(`Invalid data for issue: ${name}`);
                console.error(`Parsed Estimated Time: ${estimatedTime}`);
                console.error(`Parsed Resolution Time: ${resolutionTime}`);
            }
        } else {
            console.error('Row does not have exactly 6 cells:', row);
        }
    });

    const seriesData = Object.keys(issueData).map(priority => {
        return {
            name: priority,
            data: issueData[priority].map(issue => ({
                x: issue.x,
                y: issue.y*(-1),
                name: issue.name,
                created: issue.created,
                resolved: issue.resolved
            })),
            color: getColor(priority)
        };
    });

    function getColor(priority) {
        const colors = {
            'Critical': '#FF0000', // Red
            'High': '#0000FF', // Blue
            'Medium': '#FFFF00', // Yellow
            'Low': '#008000', // Green
            'Not Prioritized': '#FFA500', // Orange
        };
        return colors[priority] || '#000000'; // Default to black if not found
    }

    Highcharts.chart('scatter-container', {
        chart: {
            type: 'scatter',
            zoomType: 'xy'
        },
        title: {
            text: 'Issue Resolution Times'
        },
        xAxis: {
            title: {
                text: 'Estimated Time (Hours)'
            }
        },
        yAxis: {
            title: {
                text: 'Issue Resolution Time (Hours)'
            }
        },
        tooltip: {
            formatter: function () {
                // Ensure that data is correctly accessed and displayed
                return `<b>${this.point.name}</b><br>
                        Estimated Time: ${this.x} hours<br>
                        Resolution Time: ${this.y} hours<br>
                        Created: ${this.point.created || 'N/A'}<br>
                        Resolved: ${this.point.resolved || 'N/A'}`;
            }
        },
        series: seriesData
    });
}

function change_graph_type() {
    if (graph1 == 'bar') {
        graph1 = 'pie';
        var table = document.getElementById('datatable');
        var rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
        var data = [];

        for (var i = 0; i < rows.length; i++) {
            var cells = rows[i].getElementsByTagName('td');
            var type = cells[0].innerText;
            var open = parseFloat(cells[1].innerText); //issues open
            var closed = parseFloat(cells[2].innerText); //issues closed

            data.push({
                name: type,
                y: open + closed,
            });
        }
 
        Highcharts.chart('container', {
            chart: {
                type: 'pie'
            },
            title: {
                text: 'Distribution of open issues in the project'
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
                name: 'Total issues',
                colorByPoint: true,
                data: data
            }]
        });
    } else {
        graph1 = 'bar';
        initializeChart();
    }


    // Check for forced colors mode
    if (window.matchMedia && window.matchMedia('(forced-colors: active)').matches) {
        // Handle forced colors mode
        console.log('Forced colors mode active');
    }
}


function showOverview(projectId) {
    fetch(`overview/${projectId}/`)
    .then(response => response.text())
    .then(data => {
        const overviewContent = document.getElementById("overview-content");
        if (overviewContent) {
            overviewContent.innerHTML = data;

            // Initialize charts after content is set
            initializeChart();
            initializeScatterChart();
        } else {
            console.error('Overview content element not found.');
        } 
        document.getElementById("measurements-content").innerHTML = ''; 
        document.getElementById("admin-content").innerHTML = ''; 
        initializeChart();
        new DataTable('#databaseOver');
        initializeScatterChart();
    })
    .catch(error => console.error('Error fetching overview:', error));
}

function showMeasurements(projectId) {
    
    fetch(`measurements/${projectId}/`)
        .then(response => response.text())
        .then(data => {
            const measurementContent = document.getElementById("measurements-content");
            if (measurementContent) {
                measurementContent.innerHTML = data;
                new DataTable('#result-table-1');
                new DataTable('#result-table-2');
                new DataTable('#result-table-3');
                new DataTable('#result-table-4');
                new DataTable('#result-table-5');
                new DataTable('#result-table-6');
               
            } else {
                console.error('measurements content element not found.');
            } 
       
            document.getElementById("overview-content").innerHTML = ''; // Clear the overview content
            document.getElementById("admin-content").innerHTML = ''; // Clear the admin content
            
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

            // Check for forced colors mode
            if (window.matchMedia && window.matchMedia('(forced-colors: active)').matches) {
                // Handle forced colors mode
                console.log('Forced colors mode active');
            }
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

function showProfilePage() {
    fetch(`ProfilePage/`)
        .then(response => response.text())
        .then(data => {
            document.getElementById("profile-content").innerHTML = data;
            document.getElementById("measurements-content").innerHTML = ''; // Clear the measurements content
            document.getElementById("overview-content").innerHTML = ''; // Clear the overview content
            document.getElementById("admin-content").innerHTML = ''; // Clear the overview content
        })
        .catch(error => console.error('Error fetching USer profile page:', error));
}
