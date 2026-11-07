// Shared shopper journey for every k6 test (Group 02).
//
// A virtual user behaves like a real shopper on the storefront: browse the
// catalog, search, open a category, look at a product, then put it in their own
// cart. It NEVER checks out, so load tests create no orders on the shared server.
import http from 'k6/http';
import { check, group, sleep } from 'k6';

export const BASE = (__ENV.STORE_API_URL || 'http://157.85.104.96/shop/wp-json/wc/store/v1').replace(/\/$/, '');

// Sample catalog data (ids from GET /products and /products/categories).
const SIMPLE_PRODUCTS = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 30, 31];
const CATEGORIES = [22, 23, 25, 27];
const KEYWORDS = ['hoodie', 'shirt', 'beanie', 'cap', 'logo', 'album'];

const pick = (list) => list[Math.floor(Math.random() * list.length)];
const think = () => sleep(1 + Math.random() * 2); // 1-3 s, like a person reading the page

function isJsonList(r) {
  try {
    return Array.isArray(r.json());
  } catch (e) {
    return false;
  }
}

// `tags` is a function called before every request, so each request is labelled
// with the load level or time window it was really sent in (one journey takes
// about 12 s and can cross from one stage into the next).
export function shopperJourney(tags = () => ({})) {
  group('browse catalog', () => {
    const r = http.get(`${BASE}/products?per_page=20`, { tags: { ...tags(), name: 'GET /products' } });
    check(r, {
      'browse: status 200': (res) => res.status === 200,
      'browse: list of products': (res) => isJsonList(res) && res.json().length > 0,
    });
  });
  think();

  group('search', () => {
    const r = http.get(`${BASE}/products?search=${pick(KEYWORDS)}`, { tags: { ...tags(), name: 'GET /products?search' } });
    check(r, { 'search: status 200': (res) => res.status === 200 && isJsonList(res) });
  });
  think();

  group('category', () => {
    const r = http.get(`${BASE}/products?category=${pick(CATEGORIES)}`, { tags: { ...tags(), name: 'GET /products?category' } });
    check(r, { 'category: status 200': (res) => res.status === 200 && isJsonList(res) });
  });
  think();

  const productId = pick(SIMPLE_PRODUCTS);
  group('product detail', () => {
    const r = http.get(`${BASE}/products/${productId}`, { tags: { ...tags(), name: 'GET /products/{id}' } });
    check(r, {
      'detail: status 200': (res) => res.status === 200,
      'detail: right product': (res) => res.status === 200 && res.json('id') === productId,
    });
  });
  think();

  group('add to cart', () => {
    // Each iteration gets its own cart token = its own cart.
    const cart = http.get(`${BASE}/cart`, { tags: { ...tags(), name: 'GET /cart' } });
    check(cart, { 'cart: got Cart-Token': (res) => res.status === 200 && !!res.headers['Cart-Token'] });
    const headers = {
      'Content-Type': 'application/json',
      'Cart-Token': cart.headers['Cart-Token'],
      Nonce: cart.headers['Nonce'] || '',
    };
    const add = http.post(`${BASE}/cart/add-item`, JSON.stringify({ id: productId, quantity: 1 }), {
      headers,
      tags: { ...tags(), name: 'POST /cart/add-item' },
    });
    check(add, {
      'add: status 201': (res) => res.status === 201,
      'add: item in cart': (res) => res.status === 201 && res.json('items_count') === 1,
    });
  });
  think();
}
