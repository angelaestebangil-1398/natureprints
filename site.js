/* =====================================================================
   Site logic: header/footer, product cards, room previews, cart.
   You normally don't need to edit this file.
   ===================================================================== */

/* ---------- Helpers ---------- */
const $ = (sel, root = document) => root.querySelector(sel);
const money = (n) => SHOP.currency + (Number.isInteger(n) ? n : n.toFixed(2));
const catName = (id) => (CATEGORIES.find((c) => c.id === id) || {}).name || "";
const sizesFor = (p) => SIZES.filter((s) => !p.sizes || p.sizes.includes(s.id));
const finishById = (id) => FINISHES.find((f) => f.id === id) || FINISHES[0];
const sizeById = (id) => SIZES.find((s) => s.id === id) || SIZES[0];
const fromPrice = (p) => Math.min(...sizesFor(p).map((s) => s.price));
const unitPrice = (sizeId, finishId) => sizeById(sizeId).price + finishById(finishId).extra;

// Real print dimensions (width × height in cm) depending on photo orientation
function dims(p, size) {
  return p.orientation === "portrait" ? { w: size.short, h: size.long } : { w: size.long, h: size.short };
}
const sizeLabel = (p, size) => { const d = dims(p, size); return `${d.w} × ${d.h} cm`; };

const ICON = {
  cart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M5 8h14l-1.2 11.2a1 1 0 0 1-1 .8H7.2a1 1 0 0 1-1-.8L5 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>',
  menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
  close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 6l12 12M18 6 6 18"/></svg>',
  paper: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="5" y="3" width="14" height="18" rx="1"/><path d="M8 15l3-3 2 2 3-3"/></svg>',
  leaf: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M5 19C5 9 11 5 20 4c-1 9-5 15-15 15Z"/><path d="M5 19 13 11"/></svg>',
  pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12Z"/><circle cx="12" cy="9" r="2.5"/></svg>',
  truck: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 6h11v10H3zM14 10h4l3 3v3h-7"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/></svg>',
};

/* ---------- Room previews ----------
   Drawn to scale: a bigger print size really looks bigger on the wall. */
const ROOMS = {
  living: {
    wallCm: 320, // width of wall shown (room height = 240 cm)
    printBottom: 53.7, // % from bottom of the room
    furniture: `
      <svg class="furniture" viewBox="0 0 400 300" preserveAspectRatio="none" aria-hidden="true">
        <!-- side table + lamp -->
        <rect x="22" y="214" width="40" height="5" fill="#6b4a2e"/><rect x="38" y="219" width="8" height="45" fill="#6b4a2e"/>
        <rect x="30" y="196" width="24" height="18" rx="2" fill="#d8a531"/>
        <!-- sofa -->
        <rect x="78" y="176" width="244" height="58" rx="10" fill="#cdbfa6"/>
        <rect x="70" y="200" width="30" height="58" rx="9" fill="#c2b398"/>
        <rect x="300" y="200" width="30" height="58" rx="9" fill="#c2b398"/>
        <rect x="96" y="214" width="208" height="38" rx="6" fill="#d8ccb5"/>
        <rect x="200" y="214" width="1.4" height="38" fill="#c2b398"/>
        <rect x="114" y="190" width="40" height="30" rx="7" fill="#4e5b39"/>
        <rect x="248" y="190" width="40" height="30" rx="7" fill="#7a5535"/>
        <rect x="88" y="256" width="5" height="9" fill="#5a3f27"/><rect x="307" y="256" width="5" height="9" fill="#5a3f27"/>
        <!-- plant -->
        <path d="M352 226h30l-4 38h-22z" fill="#a0673f"/>
        <path d="M367 226c-2-24-18-38-24-58 14 10 22 30 24 58Zm0 0c2-28 6-48 18-66-2 22-10 44-18 66Zm0 0c-6-18-22-24-30-28 14 2 26 10 30 28Zm0 0c4-16 16-26 28-30-8 10-20 18-28 30Z" fill="#4e5b39"/>
        <!-- rug -->
        <ellipse cx="200" cy="284" rx="150" ry="10" fill="#e9dfcb" opacity=".8"/>
      </svg>`,
  },
  bath: {
    wallCm: 240, // room height = 180 cm
    printBottom: 56.7,
    furniture: `
      <div class="tiles"></div>
      <svg class="furniture" viewBox="0 0 400 300" preserveAspectRatio="none" aria-hidden="true">
        <!-- bathtub -->
        <path d="M66 172h268v40c0 28-22 44-50 44H116c-28 0-50-16-50-44z" fill="#fbfaf7"/>
        <path d="M66 172h268v6H66z" fill="#e8e3d9"/>
        <rect x="96" y="254" width="8" height="10" rx="2" fill="#b8913a"/><rect x="296" y="254" width="8" height="10" rx="2" fill="#b8913a"/>
        <!-- tap -->
        <path d="M300 172v-22h16" stroke="#b8913a" stroke-width="4" fill="none"/>
        <!-- towel on tub -->
        <path d="M120 170h40v42h-40z" fill="#d8a531" opacity=".9"/>
        <!-- stool + plant -->
        <rect x="350" y="222" width="34" height="5" fill="#7a5535"/><rect x="354" y="227" width="4" height="37" fill="#7a5535"/><rect x="376" y="227" width="4" height="37" fill="#7a5535"/>
        <path d="M356 204h22l-3 18h-16z" fill="#f2efe8" stroke="#d9d2c4"/>
        <path d="M367 204c-10-14-22-16-28-18 12 0 22 6 28 18Zm0 0c0-16 6-28 16-34-4 12-10 22-16 34Zm0 0c-2-18-6-30-12-38 8 8 12 20 12 38Z" fill="#4e5b39"/>
      </svg>`,
  },
};

ROOMS.office = {
  wallCm: 280, // room height = 210 cm
  printBottom: 62,
  furniture: `
    <svg class="furniture" viewBox="0 0 400 300" preserveAspectRatio="none" aria-hidden="true">
      <!-- bookshelf -->
      <rect x="14" y="120" width="56" height="144" fill="#7a5535"/>
      <rect x="19" y="126" width="46" height="132" fill="#5f4129"/>
      <rect x="19" y="158" width="46" height="4" fill="#7a5535"/><rect x="19" y="194" width="46" height="4" fill="#7a5535"/><rect x="19" y="228" width="46" height="4" fill="#7a5535"/>
      <rect x="23" y="134" width="6" height="24" fill="#d8a531"/><rect x="30" y="138" width="5" height="20" fill="#e9dfcb"/><rect x="36" y="132" width="7" height="26" fill="#4e5b39"/><rect x="48" y="140" width="12" height="18" rx="6" fill="#a9b79a"/>
      <rect x="23" y="172" width="8" height="22" fill="#e9dfcb"/><rect x="32" y="176" width="6" height="18" fill="#a0673f"/><rect x="40" y="170" width="5" height="24" fill="#d8a531"/>
      <rect x="24" y="214" width="34" height="14" fill="#cdbfa6"/><rect x="26" y="240" width="9" height="18" fill="#4e5b39"/><rect x="37" y="244" width="7" height="14" fill="#e9dfcb"/>
      <!-- desk -->
      <rect x="100" y="157" width="200" height="7" fill="#9c7650"/>
      <rect x="106" y="164" width="5" height="100" fill="#6b4a2e"/><rect x="289" y="164" width="5" height="100" fill="#6b4a2e"/>
      <rect x="230" y="164" width="60" height="30" fill="#8a6644"/><rect x="256" y="177" width="10" height="3" rx="1.5" fill="#d8a531"/>
      <!-- lamp -->
      <path d="M128 157h20M138 157v-18l12-8" stroke="#2b2720" stroke-width="2.5" fill="none"/><path d="M145 125l15 5-6 11z" fill="#d8a531"/>
      <!-- laptop + books + mug -->
      <path d="M178 157l6-26h44l6 26z" fill="#c9c3b6"/><rect x="172" y="155" width="68" height="3" fill="#a9a397"/>
      <rect x="250" y="147" width="32" height="5" fill="#4e5b39"/><rect x="252" y="142" width="28" height="5" fill="#d8a531"/><rect x="249" y="152" width="34" height="5" fill="#a0673f"/>
      <!-- chair -->
      <rect x="172" y="186" width="62" height="56" rx="10" fill="#4e5b39"/>
      <rect x="200" y="242" width="6" height="16" fill="#2b2720"/><rect x="180" y="258" width="46" height="5" rx="2.5" fill="#2b2720"/>
      <!-- plant -->
      <path d="M340 236h26l-3 28h-20z" fill="#a0673f"/>
      <path d="M353 236c-4-20-16-30-22-40 12 6 20 20 22 40Zm0 0c2-22 8-36 18-46-4 16-10 30-18 46Zm0 0c0-24-2-40-8-54 8 12 10 30 8 54Z" fill="#4e5b39"/>
    </svg>`,
};

function roomHTML(p, sizeId, type = "living") {
  const room = ROOMS[type];
  const size = sizeById(sizeId);
  const d = dims(p, size);
  const roomH = room.wallCm * 0.75;
  return `
    <div class="room room-${type}">
      <div class="wall"></div><div class="floor"></div>
      ${room.furniture}
      <div class="print" style="width:${(d.w / room.wallCm) * 100}%;height:${(d.h / roomH) * 100}%;bottom:${room.printBottom}%">
        <img src="${p.thumb}" alt="">
      </div>
    </div>`;
}

/* ---------- Real room pictures (built by tools/build_mockups.py) ---------- */
const mockFor = (p) => (typeof MOCKUPS !== "undefined" ? MOCKUPS[p.id] : null);

// Picture of a room for the chosen size; if that wall can't fit it, the biggest size that fits.
let FRAME = "white"; // frame colour shown in room pictures (preview only, frames are not sold)
try { FRAME = localStorage.getItem("pl_frame") || "white"; } catch {}
function setFrame(f) { FRAME = f; try { localStorage.setItem("pl_frame", f); } catch {} }

function roomShot(room, sizeId, frame = FRAME) {
  const order = SIZES.map((s) => s.id);
  let i = order.indexOf(sizeId);
  while (i >= 0 && !room.sizes[order[i]]) i--;
  const shown = i >= 0 ? order[i] : Object.keys(room.sizes)[0];
  const pic = room.sizes[shown];
  return { src: typeof pic === "string" ? pic : pic[frame] || pic.white, shown };
}

/* ---------- Sets: two prints that go together ---------- */
const allSets = () => (typeof SETS !== "undefined" ? SETS : []);
const setPrice = (st, finishId = FINISHES[0].id) => st.items.length * unitPrice(st.size, finishId);
function setCardHTML(st, frame = "white") {
  const [a, b] = st.items.map((id) => PRODUCTS.find((x) => x.id === id));
  return `
    <div class="set-card">
      <div class="set-img"><img src="${st.images[frame] || st.images.white}" alt="${st.title}: ${a.title} and ${b.title}" loading="lazy"></div>
      <div class="set-body">
        <h3>${st.title}</h3>
        <p class="muted">Set of 2 · <a href="product.html?id=${a.id}">${a.title}</a> + <a href="product.html?id=${b.id}">${b.title}</a></p>
        <div class="set-buy"><span>${sizeLabel(a, sizeById(st.size))} each · <b>${money(setPrice(st))}</b></span>
        <button class="btn" data-add-set="${st.id}">Add set to cart</button></div>
      </div>
    </div>`;
}
function addSetToCart(setId, finishId = FINISHES[0].id) {
  const st = allSets().find((x) => x.id === setId);
  if (!st) return;
  const cart = getCart();
  st.items.forEach((id) => {
    const found = cart.find((i) => i.id === id && i.size === st.size && i.finish === finishId);
    if (found) found.qty += 1; else cart.push({ id, size: st.size, finish: finishId, qty: 1 });
  });
  saveCart(cart);
  openCart();
}
document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-add-set]");
  if (b) addSetToCart(b.dataset.addSet, b.dataset.finish);
});
const photoView = (src, alt) => `<div class="view-photo"><img src="${src}" alt="${alt}"></div>`;

/* ---------- Product card ---------- */
function cardHTML(p) {
  const midSize = sizesFor(p)[Math.min(1, sizesFor(p).length - 1)].id;
  const m = mockFor(p);
  if (m) {
    return `
    <a class="card" href="product.html?id=${p.id}">
      <div class="stage photo">
        <img src="${m.print}" alt="${p.title}" loading="lazy">
        <img class="hover" src="${roomShot(m.rooms[0], midSize).src}" alt="" loading="lazy">
      </div>
      <div class="info">
        <div><h3>${p.title}</h3><div class="cat-name">${catName(p.category)}</div></div>
        <div class="from">from ${money(fromPrice(p))}</div>
      </div>
    </a>`;
  }
  return `
    <a class="card" href="product.html?id=${p.id}">
      <div class="stage">
        <div class="paper ${p.orientation}"><img src="${p.thumb}" alt="${p.title}" loading="lazy"></div>
        ${roomHTML(p, midSize, p.room || "living")}
      </div>
      <div class="info">
        <div><h3>${p.title}</h3><div class="cat-name">${catName(p.category)}</div></div>
        <div class="from">from ${money(fromPrice(p))}</div>
      </div>
    </a>`;
}

/* ---------- Header, footer, drawer (same on every page) ---------- */
function renderLayout() {
  const page = document.body.dataset.page;
  const cat = new URLSearchParams(location.search).get("cat");
  const navLinks = [
    { href: "shop.html", label: "Shop all", active: page === "shop" && !cat },
    ...CATEGORIES.map((c) => ({ href: `shop.html?cat=${c.id}`, label: c.name, active: cat === c.id })),
    { href: "about.html", label: "About me", active: page === "about" },
  ];

  document.body.insertAdjacentHTML("afterbegin", `
    <div class="announce">Free worldwide shipping on orders over <b>${money(SHOP.freeShippingFrom)}</b> · Printed &amp; shipped from ${SHOP.city}</div>
    <header class="header">
      <div class="wrap">
        <button class="icon-btn menu-btn" aria-label="Menu" data-open-menu>${ICON.menu}</button>
        <a class="logo" href="index.html">${SHOP.name}<small>${SHOP.tagline}</small></a>
        <nav class="nav">${navLinks.map((l) => `<a href="${l.href}" class="${l.active ? "active" : ""}">${l.label}</a>`).join("")}</nav>
        <div class="header-actions">
          <button class="icon-btn" aria-label="Cart" data-open-cart>${ICON.cart}<span class="cart-count" data-cart-count></span></button>
        </div>
      </div>
    </header>
    <div class="mobile-nav" data-menu>
      <button class="icon-btn" aria-label="Close menu" data-close-menu>${ICON.close}</button>
      ${navLinks.map((l) => `<a href="${l.href}">${l.label}</a>`).join("")}
    </div>`);

  document.body.insertAdjacentHTML("beforeend", `
    <footer class="footer">
      <div class="wrap">
        <div class="footer-grid">
          <div>
            <a class="logo" href="index.html">${SHOP.name}</a>
            <p>Nature is closer than you think. Photographs of the wild life around our cities, printed as fine art in ${SHOP.city} and shipped worldwide.</p>
          </div>
          <div>
            <h4>Shop</h4>
            <a href="shop.html">All prints</a>
            ${CATEGORIES.map((c) => `<a href="shop.html?cat=${c.id}">${c.name}</a>`).join("")}
          </div>
          <div>
            <h4>Help</h4>
            <a href="about.html">About me</a>
            <a href="policies.html">Shipping &amp; returns</a>
            <a href="policies.html#privacy">Privacy</a>
            <a href="mailto:${SHOP.email}">Contact</a>
          </div>
        </div>
        <div class="footer-bottom">
          <span>© ${new Date().getFullYear()} ${SHOP.name}. All photographs are copyrighted.</span>
          <span><a href="${SHOP.instagram}" style="display:inline">Instagram</a></span>
        </div>
      </div>
    </footer>
    <div class="overlay" data-overlay></div>
    <aside class="drawer" data-drawer aria-label="Cart">
      <div class="drawer-head"><h2>Your cart</h2><button class="icon-btn" aria-label="Close cart" data-close-cart>${ICON.close}</button></div>
      <div class="ship-bar" data-ship-bar></div>
      <div class="drawer-items" data-cart-items></div>
      <div class="drawer-foot" data-cart-foot></div>
    </aside>
    <div class="toast" data-toast></div>`);

  document.addEventListener("click", (e) => {
    if (e.target.closest("[data-open-cart]")) openCart();
    if (e.target.closest("[data-close-cart]") || e.target.matches("[data-overlay]")) closeCart();
    if (e.target.closest("[data-open-menu]")) $("[data-menu]").classList.add("open");
    if (e.target.closest("[data-close-menu]")) $("[data-menu]").classList.remove("open");
  });
}

function toast(msg) {
  const t = $("[data-toast]");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.remove("show"), 2200);
}

/* ---------- Cart (saved in the browser) ---------- */
const CART_KEY = "pl_cart";
function getCart() {
  try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; } catch { return []; }
}
function saveCart(cart) {
  try { localStorage.setItem(CART_KEY, JSON.stringify(cart)); } catch {}
  renderCart();
}
function addToCart(id, sizeId, finishId, qty = 1) {
  const cart = getCart();
  const found = cart.find((i) => i.id === id && i.size === sizeId && i.finish === finishId);
  if (found) found.qty += qty; else cart.push({ id, size: sizeId, finish: finishId, qty });
  saveCart(cart);
  openCart();
}
function cartTotal(cart) {
  return cart.reduce((sum, i) => sum + unitPrice(i.size, i.finish) * i.qty, 0);
}
function openCart() { $("[data-drawer]").classList.add("open"); $("[data-overlay]").classList.add("open"); }
function closeCart() { $("[data-drawer]").classList.remove("open"); $("[data-overlay]").classList.remove("open"); }

function renderCart() {
  const cart = getCart().filter((i) => PRODUCTS.some((p) => p.id === i.id));
  const count = cart.reduce((n, i) => n + i.qty, 0);
  document.querySelectorAll("[data-cart-count]").forEach((el) => { el.textContent = count || ""; el.dataset.n = count; });

  const total = cartTotal(cart);
  const left = SHOP.freeShippingFrom - total;
  $("[data-ship-bar]").innerHTML = (left > 0
    ? `You're <b>${money(left)}</b> away from free shipping`
    : `🎉 Your order ships <b>free</b>`) +
    `<div class="track"><div class="fill" style="width:${Math.min(100, (total / SHOP.freeShippingFrom) * 100)}%"></div></div>`;

  if (!cart.length) {
    $("[data-cart-items]").innerHTML = `<div class="drawer-empty"><p>Your cart is empty.</p><a class="btn btn-outline" href="shop.html">Browse prints</a></div>`;
    $("[data-cart-foot]").innerHTML = "";
    return;
  }

  $("[data-cart-items]").innerHTML = cart.map((i, idx) => {
    const p = PRODUCTS.find((x) => x.id === i.id);
    return `
      <div class="line">
        <img src="${p.thumb}" alt="">
        <div>
          <h4>${p.title}</h4>
          <div class="meta">${sizeLabel(p, sizeById(i.size))} · ${finishById(i.finish).name}</div>
          <div class="qty"><button data-q="${idx}" data-d="-1" aria-label="Less">−</button><span>${i.qty}</span><button data-q="${idx}" data-d="1" aria-label="More">+</button></div>
        </div>
        <div class="right"><span>${money(unitPrice(i.size, i.finish) * i.qty)}</span><button class="remove" data-rm="${idx}">Remove</button></div>
      </div>`;
  }).join("");

  $("[data-cart-foot]").innerHTML = `
    <div class="row"><span>Subtotal</span><span>${money(total)}</span></div>
    <div class="row muted" style="font-size:14px"><span>Shipping</span><span>${left <= 0 ? "Free" : "Calculated at checkout"}</span></div>
    <div class="row total"><span>Total</span><span>${money(total)}</span></div>
    <button class="btn btn-block" data-checkout>Checkout</button>`;

  $("[data-cart-items]").onclick = (e) => {
    const c = getCart();
    const q = e.target.closest("[data-q]");
    const rm = e.target.closest("[data-rm]");
    if (q) { const it = c[+q.dataset.q]; it.qty = Math.max(1, it.qty + +q.dataset.d); saveCart(c); }
    if (rm) { c.splice(+rm.dataset.rm, 1); saveCart(c); }
  };
  $("[data-checkout]").onclick = checkout;
}

/* STEP 2 (later): this will send the cart to Stripe Checkout.
   For now it prepares an order email so orders can already be taken. */
function checkout() {
  const cart = getCart();
  const lines = cart.map((i) => {
    const p = PRODUCTS.find((x) => x.id === i.id);
    return `- ${i.qty} × ${p.title}, ${sizeLabel(p, sizeById(i.size))}, ${finishById(i.finish).name}: ${money(unitPrice(i.size, i.finish) * i.qty)}`;
  });
  const body = `Hello,\n\nI'd like to order:\n${lines.join("\n")}\n\nSubtotal: ${money(cartTotal(cart))}\n\nName:\nShipping address:\nCountry:\nPhone:\n`;
  location.href = `mailto:${SHOP.email}?subject=${encodeURIComponent("New order")}&body=${encodeURIComponent(body)}`;
}

/* ---------- Pages ---------- */
function renderHome() {
  document.querySelectorAll("[data-ico]").forEach((el) => (el.innerHTML = ICON[el.dataset.ico]));
  const hero = PRODUCTS.find((p) => p.id === "ibex-portrait") || PRODUCTS[0];
  const second = PRODUCTS.find((p) => p.id === "orb-spider") || PRODUCTS[1];
  const secondM = mockFor(second);
  $("[data-bath-room]").innerHTML = secondM
    ? photoView(roomShot(secondM.rooms[0], "70x100").src, second.title)
    : roomHTML(second, "50x70", "office");

  $("[data-cats]").innerHTML = CATEGORIES.map((c) => {
    const items = PRODUCTS.filter((p) => p.category === c.id);
    const cover = items[items.length > 2 ? 2 : 0];
    return cover
      ? `<a class="cat" href="shop.html?cat=${c.id}"><img src="${cover.thumb}" alt="" loading="lazy"><div class="label"><h3>${c.name}</h3><span>${items.length} print${items.length > 1 ? "s" : ""}</span></div></a>`
      : `<a class="cat empty" href="shop.html?cat=${c.id}"><div class="pattern"></div><div class="label"><h3>${c.name}</h3><span>Coming soon</span></div></a>`;
  }).join("");


  const hs = $("[data-home-sets]");
  if (hs) hs.innerHTML = allSets().map((st) => setCardHTML(st, "wood")).join("");
  $("[data-featured]").innerHTML = PRODUCTS.slice(0, 6).map(cardHTML).join("");
}

function renderShop() {
  const params = new URLSearchParams(location.search);
  const cat = params.get("cat");
  const current = CATEGORIES.find((c) => c.id === cat);
  const items = PRODUCTS.filter((p) => !current || p.category === cat);
  const title = current ? current.name : "All prints";
  document.title = `${title} · ${SHOP.name}`;
  $("[data-shop-title]").textContent = title;

  const tab = (href, label, n, active) => `<a class="tab ${active ? "active" : ""}" href="${href}">${label}<span class="n">${n}</span></a>`;
  $("[data-tabs]").innerHTML =
    tab("shop.html", "All", PRODUCTS.length, !current) +
    CATEGORIES.map((c) => tab(`shop.html?cat=${c.id}`, c.name, PRODUCTS.filter((p) => p.category === c.id).length, cat === c.id)).join("");

  $("[data-results]").textContent = items.length ? `${items.length} print${items.length > 1 ? "s" : ""}` : "";
  $("[data-grid]").innerHTML = items.length
    ? items.map(cardHTML).join("")
    : "";
  $("[data-empty]").hidden = items.length > 0;
}

const ROOM_LABEL = { living: "Living room", bath: "Bathroom", office: "Office" };
const roomOrder = (p) => { const first = p.room || "living"; return [first, ...Object.keys(ROOM_LABEL).filter((r) => r !== first)]; };

function renderProduct() {
  const id = new URLSearchParams(location.search).get("id");
  const p = PRODUCTS.find((x) => x.id === id) || PRODUCTS[0];
  document.title = `${p.title} · ${SHOP.name}`;
  const sizes = sizesFor(p);
  const state = { size: sizes[Math.min(1, sizes.length - 1)].id, finish: FINISHES[0].id, qty: 1, view: 0 };
  const mySets = allSets().filter((st) => st.items.includes(p.id));

  $("[data-crumb]").innerHTML = `<a href="index.html">Home</a> / <a href="shop.html?cat=${p.category}">${catName(p.category)}</a> / ${p.title}`;

  const m = mockFor(p);
  const views = () => {
    const d = dims(p, sizeById(state.size));
    if (m) {
      return [
        { label: "Print", html: photoView(m.print, p.title) },
        ...m.rooms.map((r) => {
          const shot = roomShot(r, state.size);
          return { label: r.label, html: photoView(shot.src, `${p.title} in a ${r.label.toLowerCase()}`), shown: shot.shown };
        }),
        { label: "Detail", html: `<div class="view-detail"><img src="${p.image}" alt="Detail of ${p.title}"></div>` },
      ];
    }
    return [
      { label: "Print", html: `<div class="view-flat"><div class="paper" style="${p.orientation === "portrait" ? "width:52%" : ""}"><img src="${p.image}" alt="${p.title}" style="aspect-ratio:${d.w}/${d.h}"></div></div>` },
      ...roomOrder(p).map((r) => ({ label: ROOM_LABEL[r], html: roomHTML(p, state.size, r) })),
      { label: "Detail", html: `<div class="view-detail"><img src="${p.image}" alt="Detail of ${p.title}"></div>` },
    ];
  };

  function draw() {
    const v = views();
    $("[data-main]").innerHTML = v.map((x, i) => `<div class="view ${i === state.view ? "active" : ""}">${x.html}</div>`).join("");
    $("[data-thumbs]").innerHTML = v.map((x, i) => `<button class="thumb ${i === state.view ? "active" : ""}" data-view="${i}" aria-label="${x.label}">${x.html}<span class="thumb-label">${x.label}</span></button>`).join("");
    const cur = v[state.view];
    const shown = cur.shown || state.size;
    $("[data-caption]").textContent = state.view > 0 && state.view < v.length - 1
      ? (shown === state.size
        ? `Shown at real scale: ${sizeLabel(p, sizeById(shown))}. Frame not included.`
        : `Shown here at ${sizeLabel(p, sizeById(shown))}. Frame not included.`)
      : "";

    $("[data-price]").textContent = money(unitPrice(state.size, state.finish) * state.qty);
    $("[data-finishes]").innerHTML = FINISHES.map((f) => `<button class="opt ${f.id === state.finish ? "active" : ""}" data-finish="${f.id}">${f.name}</button>`).join("");
    $("[data-finish-note]").textContent = finishById(state.finish).note;
    $("[data-sizes]").innerHTML = sizes.map((s) => `<button class="opt ${s.id === state.size ? "active" : ""}" data-size="${s.id}">${sizeLabel(p, s)}<small>${money(s.price + finishById(state.finish).extra)}</small></button>`).join("");
    $("[data-size-label]").textContent = sizeLabel(p, sizeById(state.size));
    $("[data-finish-label]").textContent = finishById(state.finish).name;
    $("[data-qty]").textContent = state.qty;
    const fp = $("[data-frames]");
    if (fp) fp.innerHTML = `Frame in pictures: ${["white", "wood"].map((f) => `<button class="${f === FRAME ? "active" : ""}" data-frame="${f}">${f === "white" ? "White" : "Wood"}</button>`).join("")}`;
    const sb = $("[data-sets]");
    if (sb) {
      sb.hidden = !mySets.length;
      $("[data-set-cards]").innerHTML = mySets.map((st) => setCardHTML(st, FRAME)).join("");
    }
  }

  $("[data-title]").textContent = p.title;
  $("[data-cat]").textContent = catName(p.category);
  $("[data-cat]").href = `shop.html?cat=${p.category}`;
  $("[data-desc]").textContent = p.description;
  $("[data-place]").textContent = `${COLLECTION.number}: ${COLLECTION.name}`;

  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-view],[data-size],[data-finish],[data-qty-d],[data-add],[data-frame]");
    if (!t) return;
    if (t.dataset.frame) setFrame(t.dataset.frame);
    if (t.dataset.view) state.view = +t.dataset.view;
    if (t.dataset.size) state.size = t.dataset.size;
    if (t.dataset.finish) state.finish = t.dataset.finish;
    if (t.dataset.qtyD) state.qty = Math.max(1, state.qty + +t.dataset.qtyD);
    if (t.hasAttribute("data-add")) { addToCart(p.id, state.size, state.finish, state.qty); return; }
    draw();
  });

  const more = PRODUCTS.filter((x) => x.id !== p.id).sort((a, b) => (b.category === p.category) - (a.category === p.category)).slice(0, 3);
  $("[data-related]").innerHTML = more.map(cardHTML).join("");
  draw();
}

/* ---------- Start ---------- */
renderLayout();
renderCart();
({ home: renderHome, shop: renderShop, product: renderProduct }[document.body.dataset.page] || (() => {}))();
