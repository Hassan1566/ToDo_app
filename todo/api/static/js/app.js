/**
 * ToDo Application - DRF Frontend Interaction Manager
 */

// Helper: Extract CSRF Token from Django form
const getCsrfToken = () => {
    const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return tokenInput ? tokenInput.value : '';
};


// Add this function to refresh token before expiry
async function refreshJWTToken() {
    try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return;

        const response = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('jwt_token', data.access);
        }
    } catch (err) {
        console.error('Token refresh failed:', err);
    }
}

// Refresh token every 4 minutes (before 5 min expiry)
setInterval(refreshJWTToken, 4 * 60 * 1000);

// Helper: Sanitize HTML strings to prevent XSS
const escapeHtml = (text) => {
    if (!text) return '';
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
};

// Fetch Tasks from DRF ViewSet (/api/tasks/)
async function loadTasks() {
    const container = document.getElementById('tasksList');

    try {
        const response = await fetch('/api/tasks/', {
            headers: {
                'Authorization': `Bearer ${window.JWT_ACCESS_TOKEN}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch tasks');

        const tasks = await response.json();
        const taskCountElement = document.getElementById('taskCount');

        if (taskCountElement) {
            taskCountElement.innerText = `${tasks.length} task${tasks.length !== 1 ? 's' : ''}`;
        }

        if (tasks.length === 0) {
            container.innerHTML = `
                <div class="p-8 text-center text-slate-400">
                    No tasks found. Create one above to get started!
                </div>
            `;
            return;
        }

        container.innerHTML = tasks.map(task => `
            <div class="task-item p-4 flex items-start justify-between gap-4 hover:bg-slate-50 border-b border-slate-100 last:border-b-0 ${task.is_completed ? 'bg-slate-50/60' : ''}">
                <div class="flex items-start gap-3 flex-1">
                    <input type="checkbox" ${task.is_completed ? 'checked' : ''} 
                        onchange="toggleTask(${task.id}, this.checked)" 
                        class="mt-1 w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500 cursor-pointer">
                    <div>
                        <h4 class="font-medium ${task.is_completed ? 'line-through text-slate-400' : 'text-slate-800'}">
                            ${escapeHtml(task.title)}
                        </h4>
                        ${task.notes ? `<p class="text-sm text-slate-500 mt-0.5">${escapeHtml(task.notes)}</p>` : ''}
                        <div class="flex items-center gap-2 mt-1.5">
                            ${task.google_task_id
                ? `<span class="text-[10px] bg-blue-50 text-blue-600 font-medium px-2 py-0.5 rounded border border-blue-200">Google Synced</span>`
                : `<span class="text-[10px] bg-slate-100 text-slate-500 font-medium px-2 py-0.5 rounded">Local Only</span>`}
                        </div>
                    </div>
                </div>
                <button onclick="deleteTask(${task.id})" class="text-slate-400 hover:text-red-500 transition-colors p-1" title="Delete Task">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                </button>
            </div>
        `).join('');

    } catch (err) {
        console.error(err);
        container.innerHTML = `<div class="p-6 text-red-500 text-center font-medium">Failed to load tasks from server.</div>`;
    }
}

// Create Task
async function createTask(e) {
    e.preventDefault();
    const titleInput = document.getElementById('taskTitle');
    const notesInput = document.getElementById('taskNotes');

    const title = titleInput.value.trim();
    const notes = notesInput.value.trim();

    if (!title) return;

    try {
        const response = await fetch('/api/tasks/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
                'Authorization': `Bearer ${window.JWT_ACCESS_TOKEN}`,
            },
            body: JSON.stringify({ title, notes })
        });

        if (response.ok) {
            document.getElementById('createTaskForm').reset();
            loadTasks();
        } else {
            alert('Error creating task.');
        }
    } catch (err) {
        console.error('Create task failed:', err);
    }
}

// Toggle Task Completion (PATCH /api/tasks/{id}/)
async function toggleTask(id, isCompleted) {
    try {
        await fetch(`/api/tasks/${id}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
                'Authorization': `Bearer ${window.JWT_ACCESS_TOKEN}`
            },
            body: JSON.stringify({ is_completed: isCompleted })
        });
        loadTasks();
    } catch (err) {
        console.error('Toggle task failed:', err);
    }
}

// Delete Task (DELETE /api/tasks/{id}/)
async function deleteTask(id) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
        await fetch(`/api/tasks/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Authorization': `Bearer ${window.JWT_ACCESS_TOKEN}`,
            }
        });
        loadTasks();
    } catch (err) {
        console.error('Delete task failed:', err);
    }
}

// Trigger Manual Google Tasks Sync (POST /api/tasks/sync-google/)
async function syncTasks() {
    const icon = document.getElementById('syncIcon');
    if (icon) icon.classList.add('animate-spin');

    try {
        const response = await fetch('/api/tasks/sync-google/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Authorization': `Bearer ${window.JWT_ACCESS_TOKEN}`,
            }
        });
        const res = await response.json();
        alert(res.message || 'Sync completed successfully!');
        loadTasks();
    } catch (err) {
        alert('Sync failed.');
        console.error('Sync failed:', err);
    } finally {
        if (icon) icon.classList.remove('animate-spin');
    }
}

// Automatically load tasks on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
});


