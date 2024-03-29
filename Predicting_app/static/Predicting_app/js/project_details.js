document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("select-project-btn").addEventListener("click", function() {
        selectProject();
    });
});



function selectProject() {
    var projectId = document.getElementById('project-select').value;

    // Check if a project is selected
    if (projectId) {
        // Fetch project details using AJAX
        $.ajax({
            url: `/get_project_details/${projectId}`,
            method: 'GET',
            success: function(data) {
                $('#project-name').text(data.name);
                $('#project-description').text(data.description);
                // Update other elements with project details
            },
            error: function(xhr, status, error) {
                console.error(error);
            }
        });
    } else {
        // Clear project details if no project is selected
        $('#project-name').text("Project Name");
        $('#project-description').text("Project Description");
        // You can add more logic here if needed
    }
}
/*
function showOverview() {
    fetch('overview.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById("overview-content").innerHTML = data;
        })
        .catch(error => console.error('Error fetching overview:', error));
}
function showMeasurements() {
    fetch('measurements.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById("measurements-content").innerHTML = data;
        })
        .catch(error => console.error('Error fetching measurements:', error));
}
*/
// Event listener for the change event of the select dropdown
$('#project-select').change(selectProject);
