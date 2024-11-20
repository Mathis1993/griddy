import 'preline';

import { HSSelect } from 'preline/dist/preline';

// Initialize HSSelect
document.addEventListener('DOMContentLoaded', () => {
    HSSelect.autoInit();
});

// Reinitialize HSSelect after HTMX swap
document.addEventListener('htmx:afterSwap', () => {
    HSSelect.autoInit();
});