document.addEventListener("DOMContentLoaded", () => {
const form = document.getElementById("leadForm");
const responseBox = document.getElementById("responseBox");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = {
    name: form.name.value.trim(),
    email: form.email.value.trim(),
    budget: form.budget.value.trim(),
    timeline: form.timeline.value.trim(),
    description: form.description.value.trim()
  };
  console.log("Submitting:", formData);
  responseBox.innerHTML = "<p>Analyzing lead...</p>"
  try {
    const response = await fetch("http://127.0.0.1:5000/qualify-lead", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(formData)
    });

    const data = await response.json();
    console.log("Full response data:", JSON.stringify(data));
    console.log("data.result:", data.result);
    console.log("Response status:", response.status);
    console.log("Response data:", data);
    if (!response.ok) {
  responseBox.innerHTML = `
    <p style="color:red;"><strong>Error:</strong> ${data.message}</p>
  `;
  return;
}
if (!data.result) {
  responseBox.innerHTML = `<p style="color:red;">Unexpected response format.</p>`;
  console.error("Missing data.result:", data);
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
      <p>Unable to connect to backend.</p>
    `;
    console.error(error);
  }
})

});