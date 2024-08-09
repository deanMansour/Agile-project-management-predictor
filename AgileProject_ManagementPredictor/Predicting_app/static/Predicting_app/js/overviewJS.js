var currentProjectIndex = 0;
var selectedProjectName;
var uniqueProjectNames = new Set();
var projectNamesArray = [];

function extractSelectedProjectName() {
    const tableProject = document.getElementById('databaseOver');
    if (!tableProject) {
        console.error('Table with ID "databaseOver" not found');
        return;
    }

    const headers = tableProject.querySelectorAll('thead th');
    const rowsP = tableProject.querySelectorAll('tbody tr');

    let issueKeyColumnIndex = -1;
    headers.forEach((header, index) => {
        if (header.textContent.trim() === 'Issue key') {
            issueKeyColumnIndex = index;
        }
    });

    if (issueKeyColumnIndex === -1) {
        console.error('Issue key column not found');
        return;
    }

    const firstRowCells = rowsP[0].getElementsByTagName('td');
    if (firstRowCells[issueKeyColumnIndex]) {
        selectedProjectName = firstRowCells[issueKeyColumnIndex].textContent.trim().split('-')[0];
    } else {
        console.error('No Issue key found in the first row');
    }
}

function listOfProjectNames() {
    const tableA = document.getElementById('datatable3');
    if (!tableA) {
        console.error('Table with ID "datatable3" not found');
        return;
    }

    const rows2 = tableA.querySelectorAll('tbody tr');
    const headers2 = tableA.querySelectorAll('thead th');

    let projectColumnIndex = -1;
    headers2.forEach((header, index) => {
        if (header.textContent.trim() === 'Project') {
            projectColumnIndex = index;
        }
    });

    if (projectColumnIndex === -1) {
        console.error('Project column not found');
        return;
    }

    rows2.forEach((row) => {
        const cells = row.getElementsByTagName('td');
        if (cells[projectColumnIndex]) {
            const projectName = cells[projectColumnIndex].textContent.trim();
            uniqueProjectNames.add(projectName.split('-')[0]);
        }
    });

    projectNamesArray = Array.from(uniqueProjectNames);

    if (projectNamesArray.length > 0) {
        selectedProjectName = projectNamesArray[currentProjectIndex];
    }
}



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
    new DataTable('#databaseOver');
    initializeChart();
    initializeScatterChart();
    initializeBugsperCompChart();
    extractSelectedProjectName();
    listOfProjectNames();
    if (projectNamesArray.length > 0) {
        initializeVelocityChart(selectedProjectName);
        handleNavigation();
    }

    // Check for forced colors mode
    if (window.matchMedia && window.matchMedia('(forced-colors: active)').matches) {
        // Handle forced colors mode
        console.log('Forced colors mode active');
    }
});



function initializeVelocityChart(projectName) {
    const table2 = document.getElementById('datatable3');
    const rows2 = table2.querySelectorAll('tbody tr');
    var projectNameElement = document.getElementById('current-project-name');
    projectNameElement.textContent = projectName;
    var categories = [];
    var completedTasksData = [];
    var velocityData = [];

    rows2.forEach((row) => {
        const cells = row.getElementsByTagName('td');
        const projectCell = cells[0].textContent.trim();
        if (projectCell.split('-')[0] === projectName) {
            const periodStart = cells[3].innerText;
            const dateOnly = extractDate(periodStart);
            categories.push(dateOnly);
            completedTasksData.push(parseFloat(cells[5].innerText));
            velocityData.push(parseFloat(cells[7].innerText));
        }
    });

    Highcharts.chart('combo-container', {
        chart: { type: 'column' },
        title: { text: 'Project Velocity by Period' },
        xAxis: { categories: categories, title: { text: 'Period Start' } },
        yAxis: [
            {
                labels: { format: '{value}', style: { color: Highcharts.getOptions().colors[0] } },
                title: { text: 'Completed Tasks', style: { color: Highcharts.getOptions().colors[0] } }
            },
            {
                title: { text: 'Velocity', style: { color: Highcharts.getOptions().colors[1] } },
                labels: { format: '{value}', style: { color: Highcharts.getOptions().colors[1] } },
                opposite: true
            }
        ],
        series: [
            { name: 'Completed Tasks', type: 'column', data: completedTasksData, tooltip: { valueSuffix: ' tasks' } },
            { name: 'Velocity', type: 'spline', data: velocityData, yAxis: 1, tooltip: { valueSuffix: '' } }
        ]
    });
}

function handleNavigation() {
    document.getElementById('prev-project').addEventListener('click', function () {
        if (currentProjectIndex > 0) {
            currentProjectIndex--;
            selectedProjectName = projectNamesArray[currentProjectIndex];
            initializeVelocityChart(selectedProjectName);
        }
    });

    document.getElementById('next-project').addEventListener('click', function () {
        if (currentProjectIndex < projectNamesArray.length - 1) {
            currentProjectIndex++;
            selectedProjectName = projectNamesArray[currentProjectIndex];
            initializeVelocityChart(selectedProjectName);
        }
    });
}



var resolutionGraphType='scatter';

function change_resolutionGraph_type(){

    if(resolutionGraphType=='scatter'){
           
            resolutionGraphType = 'heatmap';
            const priorityList = ['Blocker','Critical', 'High', 'Medium', 'Low', 'Not Prioritized'];
            const estimateRanges = ['0-15', '16-30', '31-45', '46-60', '61-75', '76-90', '91-105', '106-120', '121-135'];
            const issueCountByRangeAndPriority = {};
            estimateRanges.forEach(range => {
                issueCountByRangeAndPriority[range] = {};
                priorityList.forEach(priority => {
                    issueCountByRangeAndPriority[range][priority] = 0;
                });
            });
            function getEstimateRangeIndex(value) {
                if (value <= 15) return 0;
                else if (value <= 30) return 1;
                else if (value <= 45) return 2;
                else if (value <= 60) return 3;
                else if (value <= 75) return 4;
                else if (value <= 90) return 5;
                else if (value <= 105) return 6;
                else if (value <= 120) return 7;
                else if (value <= 135) return 8;
                else return -1; // Invalid range
            }
    
            const tableHeat = document.getElementById('datatable2');
            if (!tableHeat) {
                console.error('Table with ID "datatable2" not found');
                return;
            }
    
            const rowsH = tableHeat.querySelectorAll('tbody tr');
            const data = [];
            console.log(issueCountByRangeAndPriority);
            rowsH.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length === 4) {
                    const issueKey = cells[0].innerText.trim();
                    const priority = cells[1].innerText.trim();
                    const estimatedTime = parseFloat(cells[2].innerText.trim());
                    const resolutionTime = parseFloat(cells[3].innerText.trim());
                    
                    // Only include valid data
                    if (!isNaN(estimatedTime) && !isNaN(resolutionTime)) {
                        const priorityIndex = priorityList.indexOf(priority);
                        const estimateIndex = getEstimateRangeIndex(estimatedTime);
                        issueCountByRangeAndPriority[estimateRanges[estimateIndex]][priority]++;
                        if (priorityIndex !== -1 && estimateIndex !== -1) {
                            data.push([priorityIndex, estimateIndex, Math.abs(resolutionTime)]); // Use absolute value
                        }
                    }
                }
            });
          
            console.log('data length: ',data.length)           

            Highcharts.chart('scatter-container', {
                chart: {
                    type: 'heatmap',
                    zoomType: 'xy'
                },
                title: {
                    text: 'Heatmap of Issue Resolution Times'
                },
                xAxis: {
                    categories: priorityList,
                    title: {
                        text: 'Priority'
                    }
                },
                yAxis: {
                    categories: estimateRanges,
                    title: {
                        text: 'Original Estimate (Hours)'
                    },
                    reversed: true // Optional: reverses the order if needed
                },
                colorAxis: {
                    min: 0,
                    minColor: '#D6FDFD',
                    maxColor: Highcharts.getOptions().colors[0],
                    title: {
                        text: 'Resolution Time (Hours)'
                    }
                },
                tooltip: {
                    formatter: function () {
                        const priority = this.series.xAxis.categories[this.point.x];
                        const estimateRange = this.series.yAxis.categories[this.point.y];
                        const resolutionTime = this.point.value;
                        return `<b>Priority: ${priority}</b><br>
                                No. of Issues: ${issueCountByRangeAndPriority[estimateRange][priority]}<br>
                                Resolution Time: ${resolutionTime} Hours<br>`;

                    }
                },
                series: [{
                    name: 'Resolution Time',
                    data: data,
                    type: 'heatmap',
                   
                }]
            });
        } else {
            resolutionGraphType = 'scatter';
            initializeScatterChart();
        }
}

   

function initializeBugsperCompChart(){

    const table = document.getElementById('datatable4');
    
    const rowsH = table.querySelectorAll('tbody tr');
    const priorityList = ['Blocker','Critical', 'High', 'Medium', 'Low', 'Not Prioritized'];
    const chartData = [];

    rowsH.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 2) {
            // Extract component name and bug counts
            const component = cells[0].innerText.trim();
            const Blocker = parseInt(cells[1].innerText.trim()) || 0;
            const Critical = parseInt(cells[2].innerText.trim()) || 0;
            const High = parseInt(cells[3].innerText.trim()) || 0;
            const Medium = parseInt(cells[4].innerText.trim()) || 0;
            const Low = parseInt(cells[5].innerText.trim()) || 0;
            const Not_Prioritized = parseInt(cells[6].innerText.trim()) || 0;
            
            chartData.push({
                component,
                Blocker,
                Critical,
                High,
                Medium,
                Low,
                Not_Prioritized
            });
        }
    });
    
    // Output the processed data
    console.log('chart length: ', chartData.length);
    
    // Configure Highcharts
    Highcharts.chart('groupBar-container', {
        chart: {
            type: 'column'
        },
        title: {
            text: 'Bugs per Component by Priority'
        },
        xAxis: {
            categories: chartData.map(item => item.component),
            title: {
                text: 'Component'
            }
        },
        yAxis: {
            min: 0,
            max: 600,
            title: {
                text: 'Number of Bugs'
            }
        },
        tooltip: {
            headerFormat: '<b>{point.x}</b><br/>',
            pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
        },
        plotOptions: {
            column: {
                stacking: 'normal'
            }
        },
        series: priorityList.map(priority => ({
            name: priority,
            data: chartData.map(item => item[priority])
        }))
    });
    
}





function initializeScatterChart() {
    const table = document.getElementById('datatable2');
    if (!table) {
        console.error('Table with ID "datatable2" not found');
        return;
    }

    const rows = table.querySelectorAll('tbody tr');
    const issueData = {
        'Critical': [],
        'High': [],
        'Medium': [],
        'Low': [],
        'Not Prioritized': [],
        'Blocker': []
    };

    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length === 4) { // Adjust based on the actual number of columns
            const issueKey = cells[0].innerText.trim();
            const priority = cells[1].innerText.trim() || 'Not Prioritized';
            const estimatedTimeStr = cells[2].innerText.trim(); // Estimated time as string
            const resolutionTimeStr = cells[3].innerText.trim(); // Resolution time as string

            // Convert strings to numbers, handle cases where conversion fails
            const estimatedTime = parseFloat(estimatedTimeStr.replace(/[^0-9.-]/g, ''));
            const resolutionTime = parseFloat(resolutionTimeStr.replace(/[^0-9.-]/g, ''));

            // Validate the numeric values
            if (!isNaN(estimatedTime) && !isNaN(resolutionTime)) {
                const issue = {
                    key: issueKey,
                    x: estimatedTime,
                    y: resolutionTime,
                };

                if (issueData.hasOwnProperty(priority)) {
                    issueData[priority].push(issue);
                } else {
                    console.error(`Unknown priority: ${priority}`);
                }
            } else {
                console.error(`Invalid data for issue: ${issueKey}`);
                console.error(`Parsed Estimated Time: ${estimatedTime}`);
                console.error(`Parsed Resolution Time: ${resolutionTime}`);
            }
        } else {
            console.error('Row does not have the expected number of cells:', row);
        }
    });

    const seriesData = Object.keys(issueData).map(priority => {
        return {
            name: priority,
            data: issueData[priority].map(issue => ({
                x: issue.x,
                y: issue.y,
                name: issue.key,
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
            'Blocker': '#800080' // Purple
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
                return `<b>${this.point.name}</b><br>
                        Estimated Time: ${this.x} hours<br>
                        Resolution Time: ${this.y} hours`;
            }
        },
        series: seriesData
    });
}
function extractDate(dateTimeString) {
    var parts = dateTimeString.split(','); // Split on comma
    return parts[0]+parts[1]; // Return only the date part
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

                // Initialize DataTables
                new DataTable('#databaseOver');
                
                // Extract project names and selected project
                extractSelectedProjectName();
                listOfProjectNames();

                // Initialize charts
                initializeChart();
                initializeScatterChart();
                initializeBugsperCompChart();
                if (projectNamesArray.length > 0) {
                    selectedProjectName = projectNamesArray[currentProjectIndex];
                    initializeVelocityChart(selectedProjectName);
                    handleNavigation();
                }

                // Clear other content
                document.getElementById("measurements-content").innerHTML = ''; 
                document.getElementById("admin-content").innerHTML = '';
            } else {
                console.error('Overview content element not found.');
            }
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
