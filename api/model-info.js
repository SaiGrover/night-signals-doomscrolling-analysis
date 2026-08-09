import registry from "../public/data/model_registry.json" with { type: "json" };

export default function handler(_request, response) {
  response.setHeader("Cache-Control", "public, max-age=300");
  response.status(200).json(registry);
}
