const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");
const input_field = document.querySelector("input");
const input_field2 = document.getElementById("pInput");
const employee_field = document.getElementById("employee");
const employee_select = document.getElementById("employeec");
const user_select = document.getElementById("userc");


sign_up_btn.addEventListener('click',() => {
  container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener('click', () => {
  container.classList.remove("sign-up-mode");
});

employee_select.addEventListener('click', () => {
  employee_field.classList.remove("hide");
})

user_select.addEventListener('click', () => {
  employee_field.classList.add("hide");
})

input_field.addEventListener('focus', () => {
  const icon = document.getElementById('user');
  icon.style.color = 'black';
});

input_field.addEventListener('blur', () => {
  const icon = document.getElementById('user');
  icon.style.removeProperty('color');
});

input_field2.addEventListener('focus', () => {
  const icon = document.getElementById('pword');
  icon.style.color = 'black';
});

input_field2.addEventListener('blur', () => {
  const icon = document.getElementById('pword')
  icon.style.removeProperty('color');
});

