const dropdown = document.getElementById("dropdown");
const list = document.querySelector('.list');
const selected = document.querySelector(".wrapper");
const selectedImg = document.querySelector(".selectedImg");
const hiddenInput = document.getElementById("emp_name");

dropdown.addEventListener('click', () => {
  list.classList.toggle('show');
  dropdown.classList.toggle('flip');
});


list.addEventListener('click', (e) => {
  const img = e.target.querySelector('.profile_pic');
  const text1 = e.target.querySelector('.employee_info');
  const valuetext = e.target.querySelector('.employee_name').textContent;

  hiddenInput.value = valuetext;
  selected.innerHTML = img.outerHTML + text1.outerHTML;
  list.classList.remove('show');
  dropdown.classList.remove('flip');

  // Filter table rows based on selected employee
  const selectedEmployee = valuetext.trim().toLowerCase();
  const rows = document.querySelectorAll('.t_row');

  rows.forEach((row) => {
    const employeeName = row.getAttribute('data-employee').trim().toLowerCase();
    if (selectedEmployee === employeeName) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
});

// Code for filtering table rows based on the initially selected employee
const emp_name = document.querySelector(".employee_name").textContent;
const selectedEmployee = emp_name.trim().toLowerCase();
const rows = document.querySelectorAll('.t_row');

rows.forEach((row) => {
  const employeeName = row.getAttribute('data-employee').trim().toLowerCase();
  if (selectedEmployee === employeeName) {
    row.style.display = '';
  } else {
    row.style.display = 'none';
  }
});

$(document).ready(function(){

  $('#date').on('change',function(){
    var selectedDate = $(this).val();
    var formattedDate = selectedDate.split('-').reverse().join('/');
    $.ajax({
      url: '/appointment',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({date: formattedDate}),
      success: function(data){
        console.log(data);
      }
    })
  })

})