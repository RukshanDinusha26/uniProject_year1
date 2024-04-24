const dropdown = document.getElementById("dropdown");
const list = document.querySelector('.list');
const selected = document.querySelector(".wrapper");
const selectedImg = document.querySelector(".selectedImg");
const hiddenInput = document.getElementById("emp_name");
const time_logo = document.getElementById("time");
const time_list = document.querySelector('.time_dropdown');
const time_cont = document.querySelector('.time_info');

dropdown.addEventListener('click', () => {
  list.classList.toggle('show');
  dropdown.classList.toggle('flip');
});

time_logo.addEventListener('click', () =>{
  time_list.classList.toggle('show');
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


time_list.addEventListener('click',(e) => {
  if(e.target.classList.contains('time_item')) {
    const timeval = e.target.textContent;
    console.log(timeval);
    console.log('picked');
  
    time_cont.textContent = timeval;
    time_list.classList.remove('show');
  }
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

  $('#date').on('input',function(){
    var selectedDate = $(this).val();
    var selectedEmployee = $('.employee_name:first').text(); //since there is multiple divs named .employee_name :first method will give us the first divs text
    $.ajax({
      url: '/appointment',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({date: selectedDate, selectedEmp: selectedEmployee}),
      success: function(data){
        $('.time_dropdown').empty();
        $.each(data.hours, function(index,hour){
          $('.time_dropdown').append("<span class='time_item'>"+hour+':00</span>'); })
      }
    })
  })

})