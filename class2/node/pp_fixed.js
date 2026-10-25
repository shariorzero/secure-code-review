const BLOCKED = new Set(["__proto__", "constructor", "prototype"]);

function safeMerge(target, source) {
  for (const key of Object.keys(source)) {
    if (BLOCKED.has(key)) continue;                 // বিপজ্জনক key বাদ
    if (typeof source[key] === "object" && source[key] !== null) {
      if (!Object.hasOwn(target, key)) target[key] = {};
      safeMerge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

const settings = {};
const userInput = JSON.parse('{"__proto__": {"isAdmin": true}}');
safeMerge(settings, userInput);
const newUser = {};
console.log("newUser.isAdmin =", newUser.isAdmin);   // undefined
