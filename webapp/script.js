const form = document.querySelector('#task-form');
const input = document.querySelector('#task-input');
const list = document.querySelector('#task-list');
const count = document.querySelector('#task-count');
const clearCompletedBtn = document.querySelector('#clear-completed');

const STORAGE_KEY = 'taskboard.tasks.v1';
let tasks = loadTasks();

render();

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const title = input.value.trim();
  if (!title) return;

  tasks.unshift({
    id: crypto.randomUUID(),
    title,
    done: false,
  });

  input.value = '';
  persist();
  render();
});

list.addEventListener('click', (event) => {
  const target = event.target;
  const taskEl = target.closest('[data-id]');
  if (!taskEl) return;

  const id = taskEl.dataset.id;
  if (target.matches('input[type="checkbox"]')) {
    tasks = tasks.map((task) => (task.id === id ? { ...task, done: target.checked } : task));
    persist();
    render();
  }

  if (target.matches('.delete-btn')) {
    tasks = tasks.filter((task) => task.id !== id);
    persist();
    render();
  }
});

clearCompletedBtn.addEventListener('click', () => {
  tasks = tasks.filter((task) => !task.done);
  persist();
  render();
});

function render() {
  list.innerHTML = '';

  if (tasks.length === 0) {
    list.innerHTML = '<li class="task"><span>No tasks yet. Add one above.</span></li>';
  } else {
    for (const task of tasks) {
      const li = document.createElement('li');
      li.className = `task ${task.done ? 'done' : ''}`;
      li.dataset.id = task.id;
      li.innerHTML = `
        <label>
          <input type="checkbox" ${task.done ? 'checked' : ''} />
          <span>${escapeHtml(task.title)}</span>
        </label>
        <button class="delete-btn" type="button">Delete</button>
      `;
      list.append(li);
    }
  }

  const openTasks = tasks.filter((task) => !task.done).length;
  count.textContent = `${openTasks} open / ${tasks.length} total`;
}

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

function loadTasks() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function escapeHtml(value) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  };
  return value.replace(/[&<>"']/g, (char) => map[char]);
}
