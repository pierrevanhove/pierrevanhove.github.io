---
author_profile: false
permalink: /pubtest.html
toc: false
toc_sticky: true
toc_label: "publications"
layout: single
---

{% include base_path %}

# Publications

<div id="papers">
  <p>Loading publications from INSPIRE-HEP…</p>
</div>

<style>
#papers h2 {
  margin-top: 1.5em;
  border-bottom: 1px solid #ddd;
  padding-bottom: 0.2em;
}
.paper-entry {
  margin-bottom: 1em;
}
.paper-entry a {
  color: #0066cc;
  text-decoration: none;
}
.paper-entry a:hover {
  text-decoration: underline;
}
.paper-authors {
  font-size: 0.9em;
  color: #555;
}
</style>

<script>
document.addEventListener("DOMContentLoaded", function() {
  const author = "Pierre+Vanhove";  // Replace with your INSPIRE author name
  const url = `https://inspirehep.net/api/literature?sort=mostrecent&size=100&q=author%3A${author}`;

  fetch(url)
    .then(r => r.json())
    .then(data => {
      const container = document.getElementById("papers");
      container.innerHTML = "";

      // Group by year
      const grouped = {};
      data.hits.hits.forEach(hit => {
        const meta = hit.metadata;
        const title = meta.titles?.[0]?.title || "(No title)";
        const year = meta.publication_info?.[0]?.year || "In preparation";
        const authors = meta.authors.map(a => a.full_name).join(", ");
        const arxiv = meta.arxiv_eprints?.[0]?.value;
        const doi = meta.dois?.[0]?.value;
        const link = arxiv ? `https://arxiv.org/abs/${arxiv}` : (doi ? `https://doi.org/${doi}` : "#");

        const entry = `
          <div class="paper-entry">
            <a href="${link}" target="_blank"><strong>${title}</strong></a><br>
            <span class="paper-authors">${authors}</span>
          </div>
        `;
        grouped[year] = grouped[year] || [];
        grouped[year].push(entry);
      });

      // Sort years descending
      const years = Object.keys(grouped).sort((a, b) => b.localeCompare(a));

      // Render grouped entries
      years.forEach(year => {
        const yearSection = document.createElement("div");
        yearSection.innerHTML = `<h2>${year}</h2>` + grouped[year].join("\n");
        container.appendChild(yearSection);
      });
    })
    .catch(err => {
      document.getElementById("papers").innerHTML =
        "<p style='color:red'>Error loading data from INSPIRE-HEP.</p>";
      console.error("INSPIRE fetch error:", err);
    });
});
</script>
