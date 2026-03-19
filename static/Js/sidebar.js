// Sidebar responsive logic
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    if (sidebar.classList.contains('-translate-x-full')) {
        sidebar.classList.remove('-translate-x-full');
        if (!overlay) createOverlay();
    } else {
        sidebar.classList.add('-translate-x-full');
        removeOverlay();
    }
}

function createOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'sidebar-overlay';
    overlay.className = 'fixed inset-0 bg-black/50 z-40 md:hidden';
    overlay.onclick = toggleSidebar;
    document.body.appendChild(overlay);
}

function removeOverlay() {
    const overlay = document.getElementById('sidebar-overlay');
    if (overlay) overlay.remove();
}
