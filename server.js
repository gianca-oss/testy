const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// L'app è interamente statica: HTML, service worker e domande (public/data/*.json).
app.use(express.static(path.join(__dirname, 'public')));

app.listen(PORT, () => {
  console.log(`EMBA Quiz running on http://localhost:${PORT}`);
});
