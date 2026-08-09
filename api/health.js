export default function handler(_request, response) {
  response.setHeader("Cache-Control", "no-store");
  response.status(200).json({ status: "ok", service: "night-signals-model-api", model_version: "2.0.0" });
}
