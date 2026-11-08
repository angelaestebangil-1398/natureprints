/* =====================================================================
   SHOP SETTINGS: the only file you need to edit day to day
   ===================================================================== */

const SHOP = {
  name: "NaturePrints",           // shop name (shown in the logo)
  tagline: "Nature, closer than you think",
  photographer: "Paolo Laitinen",
  email: "hello@example.com",
  instagram: "https://instagram.com/",
  city: "Barcelona",
  currency: "€",
  freeShippingFrom: 75,           // free shipping above this amount (€)
};

/* Categories shown in the menu and on the shop page */
const CATEGORIES = [
  { id: "birds",   name: "Birds" },
  { id: "mammals", name: "Mammals" },
  { id: "insects", name: "Insects" },
  { id: "plants",  name: "Plants & Flowers" },
];

/* Collection */
const COLLECTION = { number: "Collection 01", name: "Wildly Yours", headline: "Find the wild for your wall" };

/* Paper finishes. "extra" is added to the price (0 = same price). */
const FINISHES = [
  { id: "matte",  name: "Matte",  extra: 0, note: "Soft, no reflections, a painting-like look" },
  { id: "glossy", name: "Glossy", extra: 0, note: "Deep colours and contrast, with a subtle shine" },
];

/* Sizes in cm (short side × long side) and indicative prices (€).
   The orientation of each photo decides if it's 50×40 or 40×50. */
const SIZES = [
  { id: "40x50",  short: 40, long: 50,  price: 40 },
  { id: "50x70",  short: 50, long: 70,  price: 65 },
  { id: "70x100", short: 70, long: 100, price: 95 },
];

/* The prints. Copy a block to add a new one.
   - no: our internal photo number (not shown on the website). Never reuse a number.
   - category: one of the CATEGORIES ids above
   - place: where it was taken (internal note, not shown on the website)
   - room: which room the print is shown in first: "living", "bath" or "office"
   - orientation: "landscape" or "portrait"
   - sizes (optional): limit which sizes this photo is sold in, e.g. ["40x50","50x70"] */
const PRODUCTS = [
  {
    no: 6,
    id: "snipe",
    place: "barcelona",
    room: "office",
    title: "The Snipe",
    category: "birds",
    orientation: "landscape",
    image: "images/snipe.jpg",
    thumb: "images/snipe-sm.jpg",
    description: "A common snipe hides among the reeds, its feathers a perfect pattern of brown, cream and black, still wet with drops of water.",
  },
  {
    no: 7,
    id: "mallard-profile",
    place: "barcelona",
    room: "bath",
    title: "Emerald Profile",
    category: "birds",
    orientation: "landscape",
    image: "images/mallard-profile.jpg",
    thumb: "images/mallard-profile-sm.jpg",
    description: "A male mallard in perfect profile, its emerald head shining with drops of water against a soft pale background.",
  },
  {
    no: 8,
    id: "mallard-portrait",
    place: "barcelona",
    room: "bath",
    title: "Emerald Gaze",
    category: "birds",
    orientation: "landscape",
    image: "images/mallard-portrait.jpg",
    thumb: "images/mallard-portrait-sm.jpg",
    description: "Close and curious: a mallard looks back, every green and violet reflection of its head visible.",
  },
  {
    no: 9,
    id: "ibex-mountain",
    place: "chamonix",
    room: "living",
    title: "King of the Slope",
    category: "mammals",
    orientation: "landscape",
    image: "images/ibex-mountain.jpg",
    thumb: "images/ibex-mountain-sm.jpg",
    description: "An Alpine ibex walks down a snowy slope above Chamonix, with the blue mountains of the valley behind.",
    sizes: ["40x50", "50x70"], // smaller original, so no 70×100 (to check with the full file)
  },
  {
    no: 10,
    id: "ibex-portrait",
    place: "chamonix",
    room: "living",
    title: "Crown of the Alps",
    category: "mammals",
    orientation: "landscape",
    image: "images/ibex-portrait.jpg",
    thumb: "images/ibex-portrait-sm.jpg",
    description: "An Alpine ibex in golden autumn light, its huge curved horns drawn against the soft blue of the mountains.",
  },
  {
    no: 2,
    id: "mallard-hen",
    place: "paris",            // TO CONFIRM: where was it taken?
    title: "Among the Yellow Flowers",
    category: "birds",
    orientation: "landscape",
    image: "images/mallard-hen.jpg",
    thumb: "images/mallard-hen-sm.jpg",
    description: "A female mallard rests in a pond full of yellow water flowers, her feathers glowing in warm brown and a flash of blue.",
  },
  {
    no: 1,
    id: "mallard-drake",
    place: "paris",            // TO CONFIRM: where was it taken?
    title: "The Preening Drake",
    category: "birds",
    orientation: "landscape",
    image: "images/mallard-drake.jpg",
    thumb: "images/mallard-drake-sm.jpg",
    description: "A male mallard grooms his feathers, showing off an emerald head and an electric violet wing.",
  },
  {
    no: 3,
    id: "parakeet",
    place: "barcelona",            // TO CONFIRM: where was it taken?
    title: "Upside Down",
    category: "birds",
    orientation: "landscape",
    image: "images/parakeet.jpg",
    thumb: "images/parakeet-sm.jpg",
    description: "A ring-necked parakeet hangs upside down from a beech branch, busy with the autumn seeds.",
  },
  {
    no: 4,
    id: "crested-tit",
    place: "chamonix",            // TO CONFIRM: where was it taken?
    title: "The Crested Tit",
    category: "birds",
    orientation: "landscape",
    image: "images/crested-tit.jpg",
    thumb: "images/crested-tit-sm.jpg",
    description: "A crested tit with a seed in its beak, caught in soft light among cypress branches.",
    sizes: ["40x50", "50x70"], // smaller original, so no 70×100
  },
  {
    no: 5,
    id: "orb-spider",
    place: "barcelona",            // TO CONFIRM: where was it taken?
    title: "The Golden Orb",
    category: "insects",
    orientation: "landscape",
    image: "images/orb-spider.jpg",
    thumb: "images/orb-spider-sm.jpg",
    description: "A garden orb spider waits on a curled leaf, every hair and detail in sharp focus.",
  },
];
