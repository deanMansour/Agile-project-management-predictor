

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
                text: 'distribution of issues in the project'
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
  
  function showOverview(projectId) {
    fetch(`overview/${projectId}/`)
        .then(response => response.text())
        .then(data => {
            document.getElementById("overview-content").innerHTML = data;
            document.getElementById("measurements-content").innerHTML = ''; // Clear the measurements content
            document.getElementById("admin-content").innerHTML = ''; // Clear the admin content
            initializeChart(); // Initialize the chart after loading content
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
        })
        .catch(error => console.error('Error fetching measurements:', error));
  }
  
  function showAdminEditor() {
    fetch('admin_OR_user_MainPage.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById("admin-content").innerHTML = data;
            document.getElementById("measurements-content").innerHTML = ''; // Clear the measurements content
            document.getElementById("overview-content").innerHTML = ''; // Clear the overview content
        })
        .catch(error => console.error('Error fetching admin editor:', error));
  }
  
  document.addEventListener('DOMContentLoaded', function () {
    initializeChart();
});