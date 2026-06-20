const form = document.getElementById("leadForm");
const responseBox = document.getElementById("responseBox");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = {
    name: form.name.value,
    email: form.email.value,
    budget: form.budget.value,
    timeline: form.timeline.value,
    description: form.description.value
  };
  responseBox.innerHTML = "<p>Submitting lead...</p>"
  try {
    const response = await fetch("http://127.0.0.1:5000/qualify-lead", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(formData)
    });

    const data = await response.json();
    if (!response.ok) {
      responseBox.innerHTML = `
        <p>❌ ${data.message}</p>
      `;
      return;
    }
    responseBox.innerHTML = `
      <h3>Lead Qualification Result</h3>
      <p><strong>Status:</strong> ${data.message}</p>
      <p><strong>Score:</strong> ${data.result.score}</p>
      <p><strong>Label:</strong> ${data.result.label}</p>
      <p><strong>Summary:</strong> ${data.result.summary}</p>
    `;
    form.reset();
  } catch (error) {
    responseBox.innerHTML = `
      <p>❌ Unable to connect to backend.</p>
    `;
    console.error(error);
  }
});