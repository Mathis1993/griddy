import 'preline';

import { HSSelect } from 'preline/dist/preline';

import Swiper from 'swiper';
import { Mousewheel, Pagination } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/pagination';

// Initialize HSSelect
document.addEventListener('DOMContentLoaded', () => {
    HSSelect.autoInit();
});

// Reinitialize HSSelect after HTMX swap
document.addEventListener('htmx:afterSwap', () => {
    HSSelect.autoInit();
});

// Make Swiper available globally
window.Swiper = Swiper;
window.SwiperModules = { Mousewheel, Pagination };