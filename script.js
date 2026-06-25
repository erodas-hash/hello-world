const demoProjects = [
  {
    name: 'Implementación CRM',
    owner: 'Ana Pérez',
    plannedProgress: 65,
    actualProgress: 58,
    plannedCost: 45000,
    actualCost: 42000,
    status: 'En curso',
  },
  {
    name: 'Migración a la nube',
    owner: 'Carlos Rojas',
    plannedProgress: 80,
    actualProgress: 72,
    plannedCost: 80000,
    actualCost: 91000,
    status: 'En riesgo',
  },
  {
    name: 'Automatización de reportes',
    owner: 'María Gómez',
    plannedProgress: 100,
    actualProgress: 100,
    plannedCost: 18000,
    actualCost: 16500,
    status: 'Completado',
  },
];

let projects = JSON.parse(localStorage.getItem('project-dashboard')) || demoProjects;

const form = document.querySelector('#project-form');
const table = document.querySelector('#project-table');
const formatter = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 });

function saveProjects() {
  localStorage.setItem('project-dashboard', JSON.stringify(projects));
}

function average(values) {
  if (!values.length) return 0;
  return values.reduce((total, value) => total + value, 0) / values.length;
}

function statusClass(status) {
  return status.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replaceAll(' ', '-');
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('\"', '&quot;')
    .replaceAll("'", '&#039;');
}

function renderSummary() {
  const plannedCost = projects.reduce((total, project) => total + project.plannedCost, 0);
  const actualCost = projects.reduce((total, project) => total + project.actualCost, 0);
  const execution = plannedCost ? (actualCost / plannedCost) * 100 : 0;

  document.querySelector('#totalProjects').textContent = projects.length;
  document.querySelector('#avgPlanned').textContent = `${average(projects.map((project) => project.plannedProgress)).toFixed(1)}%`;
  document.querySelector('#avgActual').textContent = `${average(projects.map((project) => project.actualProgress)).toFixed(1)}%`;
  document.querySelector('#budgetExecution').textContent = `${execution.toFixed(1)}%`;
}

function renderProjects() {
  table.innerHTML = projects.map((project, index) => {
    const execution = project.plannedProgress ? (project.actualProgress / project.plannedProgress) * 100 : 0;

    return `
      <tr>
        <td><strong>${escapeHtml(project.name)}</strong></td>
        <td>${escapeHtml(project.owner)}</td>
        <td>${project.plannedProgress}%</td>
        <td>
          <div class="progress-bar" aria-label="Avance real ${project.actualProgress}%">
            <span style="width: ${project.actualProgress}%"></span>
          </div>
          ${project.actualProgress}%
        </td>
        <td>${execution.toFixed(1)}%</td>
        <td>${formatter.format(project.plannedCost)}</td>
        <td>${formatter.format(project.actualCost)}</td>
        <td><span class="badge badge--${statusClass(project.status)}">${escapeHtml(project.status)}</span></td>
        <td><button class="delete-button" type="button" data-index="${index}">Eliminar</button></td>
      </tr>
    `;
  }).join('');

  renderSummary();
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const data = new FormData(form);

  projects = [
    ...projects,
    {
      name: data.get('name'),
      owner: data.get('owner'),
      plannedProgress: Number(data.get('plannedProgress')),
      actualProgress: Number(data.get('actualProgress')),
      plannedCost: Number(data.get('plannedCost')),
      actualCost: Number(data.get('actualCost')),
      status: data.get('status'),
    },
  ];

  saveProjects();
  renderProjects();
  form.reset();
});

table.addEventListener('click', (event) => {
  if (!event.target.matches('.delete-button')) return;
  projects = projects.filter((_, index) => index !== Number(event.target.dataset.index));
  saveProjects();
  renderProjects();
});

document.querySelector('#reset-demo').addEventListener('click', () => {
  projects = demoProjects;
  saveProjects();
  renderProjects();
});

renderProjects();
