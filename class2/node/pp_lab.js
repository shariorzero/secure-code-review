// Prototype Pollution mini-lab (কোনো প্যাকেজ লাগে না): node pp_lab.js

// ❌ দুর্বল merge: ইউজারের অবজেক্ট বিনা যাচাইয়ে কপি করে
function merge(target, source) {
  for (const key in source) {
    if (typeof source[key] === "object" && source[key] !== null) {
      if (!target[key]) target[key] = {};
      merge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

const settings = {};                       // অ্যাপের সেটিংস
const userInput = JSON.parse('{"__proto__": {"isAdmin": true}}'); // হ্যাকারের পাঠানো JSON
merge(settings, userInput);

const newUser = {};                        // একদম নতুন, সাধারণ ইউজার
console.log("newUser.isAdmin =", newUser.isAdmin);   // প্রত্যাশা: undefined, কিন্তু...
