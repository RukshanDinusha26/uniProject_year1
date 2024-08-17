
  document.addEventListener('DOMContentLoaded', function () {
    const serviceInputs = document.querySelectorAll('input[name="service"]');
    const agentSelect = document.getElementById('select-agent');
    const hiddenServiceIdInput = document.getElementById('hidden-service-id');
    const hiddenemployeeIDInput = document.getElementById('hidden-employee-id');

    serviceInputs.forEach(service => {
      service.addEventListener('change', function () {
        agentSelect.innerHTML = '';
        hiddenServiceIdInput.value = this.getAttribute('data-service-id');

        const agents = this.getAttribute('data-agents').split(',');
        const employeeIds = this.getAttribute('data-employee-ids').split(',');

        agents.forEach(agent => {
          const option = document.createElement('option');
          option.value = agent.trim();
          option.textContent = agent.trim();
          agentSelect.appendChild(option);
        });
      });
    });
  });

  