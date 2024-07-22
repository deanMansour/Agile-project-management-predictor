//  Turn table into datatable
new DataTable('#result-table-1');
new DataTable('#result-table-2');
new DataTable('#result-table-3');
new DataTable('#result-table-4');
new DataTable('#result-table-5');
new DataTable('#result-table-6');




// Weights input
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function update_alpha(projectId){
   const mu_d = parseFloat(document.getElementById('number1-1').value);
    const v_d = parseFloat(document.getElementById('number1-2').value);
    const t_d = parseFloat(document.getElementById('number1-3').value);
    const csrfToken = getCsrfToken();


     fetch(`measurements/${projectId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
          mu_d: mu_d,
          v_d: v_d,
          t_d: t_d
        })
      })
      .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        console.log('Response received:', data);
        if (data.success) {
          alert('Alpha weights updated successfully.');
        } else {
          alert(data.message);
        }
      })
      .catch(error => console.error('Error:', error));
    }
 

    

    


$('.tooltip').hover(function() {
  var tooltipText = $(this).attr('data-tooltip');
  $(this).append('<span class="tooltiptext">' + tooltipText + '</span>');
}, function() {
  $('.tooltiptext').remove();
});


// Toggle icon on collapse/expand
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



