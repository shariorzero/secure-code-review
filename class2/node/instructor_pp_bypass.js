// ইন্সট্রাক্টর ডেমো: কোন ফিক্স কোন payload-এ টেকে/ভাঙে। AI-র ফিক্স যাচাইয়ের উদাহরণ। চালান: node instructor_pp_bypass.js
function merge(target, source, blocked) {
  for (const key in source) {
    if (blocked.includes(key)) continue;
    if (typeof source[key] === "object" && source[key] !== null) {
      if (!target[key]) target[key] = {};
      merge(target[key], source[key], blocked);
    } else target[key] = source[key];
  }
  return target;
}
const payloads = {
  proto: '{"__proto__": {"isAdmin": true}}',
  ctor:  '{"constructor": {"prototype": {"isAdmin": true}}}',
};
for (const [label, json] of Object.entries(payloads)) {
  for (const blocked of [[], ["__proto__"], ["__proto__","constructor","prototype"]]) {
    delete Object.prototype.isAdmin;
    merge({}, JSON.parse(json), blocked);
    console.log(label.padEnd(5), "blocked=" + JSON.stringify(blocked).padEnd(40), "polluted:", ({}).isAdmin === true);
  }
}
