const dropdown = document.getElementById("dropdown")

const list = document.querySelector('.list');

const selected = document.querySelector(".wrapper");

const selectedImg = document.querySelector(".selectedImg");

const hiddenInput = document.getElementById("emp_name");

const emp_name = document.querySelector(".employee_name").textContent;

console.log(emp_name)
hiddenInput.value = emp_name;


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



dropdown.addEventListener('click', ()=> {
  list.classList.toggle('show');
  dropdown.classList.toggle('flip');
})

list.addEventListener('click', (e)=>{
  const img = e.target.querySelector('.profile_pic');
  console.log(img);
  const text1 = e.target.querySelector('.employee_info');
  console.log(text1);
  const valuetext = e.target.querySelector('.employee_name').textContent;
  console.log(valuetext);
  hiddenInput.value = valuetext;
  selected.innerHTML = img.outerHTML + text1.outerHTML;
  list.classList.remove('show')
  dropdown.classList.remove('flip')

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

})

