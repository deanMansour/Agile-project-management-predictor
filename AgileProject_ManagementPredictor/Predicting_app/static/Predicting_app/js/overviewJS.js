

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
  
