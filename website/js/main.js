/* ============================================
   Everbright Cards — shared site scripts
   ============================================ */

// ---------- Product catalog ----------
const PRODUCTS = [
  { id: "bd-01", name: "Confetti Wishes", category: "birthday", emoji: "🎂", bg: "#f6ded6", price: 5.5, desc: "Hand-lettered birthday card with gold-foil confetti detail." },
  { id: "bd-02", name: "Another Trip Around the Sun", category: "birthday", emoji: "🌞", bg: "#fdf1d6", price: 6.0, desc: "Sunny illustrated card for celebrating every orbit in style." },
  { id: "bd-03", name: "Make a Wish", category: "birthday", emoji: "🎈", bg: "#eaf1f6", price: 5.0, desc: "Minimalist balloon design printed on thick cotton paper." },
  { id: "lv-01", name: "Ever Yours", category: "love", emoji: "💌", bg: "#f9dede", price: 6.5, desc: "A romantic letterpress card for anniversaries and always." },
  { id: "lv-02", name: "You + Me", category: "love", emoji: "❤️", bg: "#f6ded6", price: 5.5, desc: "Bold typographic love note with a blind-embossed heart." },
  { id: "lv-03", name: "Smitten", category: "love", emoji: "🌹", bg: "#f3e3ee", price: 6.0, desc: "Painted rose artwork, blank inside for your own words." },
  { id: "ty-01", name: "So Very Grateful", category: "thankyou", emoji: "🌻", bg: "#fdf1d6", price: 5.0, desc: "Sunflower thank-you card with a warm hand-written feel." },
  { id: "ty-02", name: "Thanks a Bunch", category: "thankyou", emoji: "💐", bg: "#eef3ea", price: 5.0, desc: "A cheerful bouquet of wildflowers in gouache." },
  { id: "ty-03", name: "You're the Best", category: "thankyou", emoji: "⭐", bg: "#eaf1f6", price: 4.5, desc: "Simple star motif that says it all — thank you." },
  { id: "hd-01", name: "Merry & Bright", category: "holiday", emoji: "🎄", bg: "#e6efe4", price: 6.0, desc: "Classic evergreen holiday card with metallic ink accents." },
  { id: "hd-02", name: "Warmest Wishes", category: "holiday", emoji: "❄️", bg: "#e8eef4", price: 5.5, desc: "Snowflake lattice design on shimmering pearl stock." },
  { id: "hd-03", name: "New Year, New Adventures", category: "holiday", emoji: "🎆", bg: "#efe6f2", price: 6.0, desc: "Fireworks over a midnight skyline to ring in the year." },
  { id: "cg-01", name: "You Did It!", category: "congrats", emoji: "🎓", bg: "#eaf1f6", price: 5.5, desc: "Graduation-ready card with a tossed-cap illustration." },
  { id: "cg-02", name: "Pop the Bubbly", category: "congrats", emoji: "🍾", bg: "#fdf1d6", price: 6.0, desc: "Champagne celebration card for promotions and wins." },
  { id: "cg-03", name: "New Home, New Memories", category: "congrats", emoji: "🏡", bg: "#eef3ea", price: 5.5, desc: "A cozy illustrated cottage for housewarming wishes." },
  { id: "bl-01", name: "Little Wonder", category: "baby", emoji: "🧸", bg: "#f9ecdd", price: 5.5, desc: "Soft teddy-bear artwork to welcome a brand-new arrival." },
  { id: "bl-02", name: "Hello, Tiny Human", category: "baby", emoji: "🌙", bg: "#e8eef4", price: 6.0, desc: "Moon-and-stars nursery palette with hand-torn edges." },
  { id: "sy-01", name: "Thinking of You", category: "sympathy", emoji: "🕊️", bg: "#eef0f2", price: 5.0, desc: "A gentle dove in soft watercolor, blank inside." },
  { id: "sy-02", name: "With Deepest Sympathy", category: "sympathy", emoji: "🌿", bg: "#e6efe4", price: 5.0, desc: "Quiet botanical sprig printed on textured ivory stock." },
  { id: "bx-01", name: "The Everyday Box Set", category: "boxset", emoji: "📦", bg: "#f0e9df", price: 24.0, desc: "Ten assorted cards for every occasion, with envelopes." },
];

const CATEGORY_LABELS = {
  birthday: "Birthday",
  love: "Love & Anniversary",
  thankyou: "Thank You",
  holiday: "Holiday",
  congrats: "Congratulations",
  baby: "New Baby",
  sympathy: "Sympathy",
  boxset: "Box Sets",
};

// ---------- Cart (persisted in localStorage) ----------
const CART_KEY = "everbright-cart";

function loadCart() {
  try {
    return JSON.parse(localStorage.getItem(CART_KEY)) || {};
  } catch {
    return {};
  }
}

function saveCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
}

function cartItemCount(cart) {
  return Object.values(cart).reduce((sum, qty) => sum + qty, 0);
}

function cartTotal(cart) {
  return Object.entries(cart).reduce((sum, [id, qty]) => {
    const product = PRODUCTS.find((p) => p.id === id);
    return product ? sum + product.price * qty : sum;
  }, 0);
}

function addToCart(id) {
  const cart = loadCart();
  cart[id] = (cart[id] || 0) + 1;
  saveCart(cart);
  updateCartUI();
  const product = PRODUCTS.find((p) => p.id === id);
  showToast(`Added "${product ? product.name : "card"}" to your cart`);
}

function changeQty(id, delta) {
  const cart = loadCart();
  cart[id] = (cart[id] || 0) + delta;
  if (cart[id] <= 0) delete cart[id];
  saveCart(cart);
  updateCartUI();
}

// ---------- Cart drawer UI ----------
function updateCartUI() {
  const cart = loadCart();
  const count = cartItemCount(cart);

  document.querySelectorAll(".cart-count").forEach((el) => {
    el.textContent = count;
  });

  const itemsEl = document.getElementById("cart-items");
  const totalEl = document.getElementById("cart-total");
  if (!itemsEl) return;

  if (count === 0) {
    itemsEl.innerHTML = '<p class="cart-empty">Your cart is empty — go find someone a lovely card! 💌</p>';
  } else {
    itemsEl.innerHTML = Object.entries(cart)
      .map(([id, qty]) => {
        const p = PRODUCTS.find((prod) => prod.id === id);
        if (!p) return "";
        return `
          <div class="cart-item">
            <div class="cart-item-art" style="background:${p.bg}">${p.emoji}</div>
            <div class="cart-item-info">
              <h4>${p.name}</h4>
              <div class="cart-item-price">$${p.price.toFixed(2)} each</div>
            </div>
            <div class="cart-qty">
              <button aria-label="Decrease quantity" onclick="changeQty('${p.id}', -1)">−</button>
              <span>${qty}</span>
              <button aria-label="Increase quantity" onclick="changeQty('${p.id}', 1)">+</button>
            </div>
          </div>`;
      })
      .join("");
  }

  if (totalEl) totalEl.textContent = `$${cartTotal(cart).toFixed(2)}`;
}

function openCart() {
  document.getElementById("cart-drawer")?.classList.add("open");
  document.getElementById("cart-overlay")?.classList.add("open");
}

function closeCart() {
  document.getElementById("cart-drawer")?.classList.remove("open");
  document.getElementById("cart-overlay")?.classList.remove("open");
}

function checkout() {
  const cart = loadCart();
  if (cartItemCount(cart) === 0) {
    showToast("Your cart is empty");
    return;
  }
  saveCart({});
  updateCartUI();
  closeCart();
  showToast("Thank you for your order! A confirmation is on its way. 🎉");
}

// ---------- Toast ----------
let toastTimer;
function showToast(message) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 2600);
}

// ---------- Product rendering ----------
function productCardHTML(p) {
  return `
    <article class="product-card" data-category="${p.category}" data-name="${p.name.toLowerCase()}">
      <div class="product-art" style="background:${p.bg}">${p.emoji}</div>
      <div class="product-info">
        <div class="product-tag">${CATEGORY_LABELS[p.category] || p.category}</div>
        <h3>${p.name}</h3>
        <p class="product-desc">${p.desc}</p>
        <div class="product-bottom">
          <span class="product-price">$${p.price.toFixed(2)}</span>
          <button class="btn btn-primary btn-small" onclick="addToCart('${p.id}')">Add to cart</button>
        </div>
      </div>
    </article>`;
}

function renderProducts(containerId, products) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = products.map(productCardHTML).join("");
}

// ---------- Shop filters ----------
function initShopPage() {
  const grid = document.getElementById("product-grid");
  if (!grid) return;

  let activeCategory = "all";
  const params = new URLSearchParams(window.location.search);
  const requested = params.get("category");
  if (requested && CATEGORY_LABELS[requested]) activeCategory = requested;

  const searchInput = document.getElementById("shop-search");

  function applyFilters() {
    const query = (searchInput?.value || "").trim().toLowerCase();
    const filtered = PRODUCTS.filter((p) => {
      const matchesCategory = activeCategory === "all" || p.category === activeCategory;
      const matchesQuery = !query || p.name.toLowerCase().includes(query) || p.desc.toLowerCase().includes(query);
      return matchesCategory && matchesQuery;
    });
    renderProducts("product-grid", filtered);
    const countEl = document.getElementById("shop-count");
    if (countEl) countEl.textContent = `${filtered.length} card${filtered.length === 1 ? "" : "s"}`;
  }

  document.querySelectorAll(".filter-btn").forEach((btn) => {
    if (btn.dataset.category === activeCategory) {
      document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    }
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeCategory = btn.dataset.category;
      applyFilters();
    });
  });

  searchInput?.addEventListener("input", applyFilters);
  applyFilters();
}

// ---------- Featured products (home page) ----------
function initHomePage() {
  const featured = ["bd-01", "lv-01", "hd-01", "bx-01"]
    .map((id) => PRODUCTS.find((p) => p.id === id))
    .filter(Boolean);
  renderProducts("featured-grid", featured);
}

// ---------- Forms ----------
function initForms() {
  const contactForm = document.getElementById("contact-form");
  contactForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    document.getElementById("contact-success")?.classList.add("visible");
    contactForm.reset();
    contactForm.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  document.querySelectorAll(".newsletter-form").forEach((form) => {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      form.reset();
      showToast("You're on the list! Welcome to the Everbright family. 💌");
    });
  });
}

// ---------- Nav ----------
function initNav() {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".main-nav");
  toggle?.addEventListener("click", () => nav?.classList.toggle("open"));

  document.getElementById("cart-overlay")?.addEventListener("click", closeCart);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeCart();
  });
}

// ---------- Boot ----------
document.addEventListener("DOMContentLoaded", () => {
  initNav();
  initHomePage();
  initShopPage();
  initForms();
  updateCartUI();
});
