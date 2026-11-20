import type { ActionFunctionArgs, LoaderFunctionArgs } from "react-router";
import { useLoaderData, useSubmit, useNavigation } from "react-router";
import { authenticate } from "../shopify.server";

interface ProductNode {
  id: string;
  title: string;
  status: string;
  totalInventory: number;
  tags: string[];
  rescueStatus?: { value: string } | null;
}

export const loader = async ({ request }: LoaderFunctionArgs) => {
  const { admin } = await authenticate.admin(request);
  const response = await admin.graphql(`#graphql
    query GetPerishableInventory {
      products(first: 25, sortKey: UPDATED_AT, reverse: true) {
        nodes {
          id
          title
          status
          totalInventory
          tags
          rescueStatus: metafield(namespace: "harvestlink", key: "rescue_status") {
            value
          }
        }
      }
    }`);
  const json = await response.json();
  return { products: (json.data?.products?.nodes ?? []) as ProductNode[] };
};

export const action = async ({ request }: ActionFunctionArgs) => {
  const { admin } = await authenticate.admin(request);
  const formData = await request.formData();
  const productId = String(formData.get("productId"));
  const intent = String(formData.get("intent"));

  if (intent === "flag_rescue") {
    await admin.graphql(`#graphql
      mutation FlagNearExpiryForRescue($id: ID!, $tags: [String!]!, $metafields: [MetafieldsSetInput!]!) {
        tagsAdd(id: $id, tags: $tags) { userErrors { field message } }
        metafieldsSet(metafields: $metafields) { userErrors { field message } }
      }`, {
      variables: {
        id: productId,
        tags: ["near-expiry-rescue", "surplus-24h"],
        metafields: [{ ownerId: productId, namespace: "harvestlink", key: "rescue_status", type: "single_line_text_field", value: "LISTED_FOR_PICKUP" }]
      }
    });
  } else if (intent === "clear_rescue") {
    await admin.graphql(`#graphql
      mutation ClearRescueFlag($id: ID!, $tags: [String!]!, $metafields: [MetafieldsSetInput!]!) {
        tagsRemove(id: $id, tags: $tags) { userErrors { field message } }
        metafieldsSet(metafields: $metafields) { userErrors { field message } }
      }`, {
      variables: {
        id: productId,
        tags: ["near-expiry-rescue", "surplus-24h"],
        metafields: [{ ownerId: productId, namespace: "harvestlink", key: "rescue_status", type: "single_line_text_field", value: "STANDARD" }]
      }
    });
  }
  return { ok: true };
};

export default function HarvestLinkDashboard() {
  const { products } = useLoaderData<typeof loader>();
  const submit = useSubmit();
  const navigation = useNavigation();
  const isSubmitting = navigation.state !== "idle";
  const flaggedCount = products.filter((p) => p.tags.includes("near-expiry-rescue") || p.rescueStatus?.value === "LISTED_FOR_PICKUP").length;

  return (
    <s-page heading="HarvestLink — Surplus & Near-Expiry Rescue">
      <s-banner tone="info">
        Flag perishable items approaching expiration within 24 hours to tag them for local food-rescue pickup via Shopify Admin GraphQL.
      </s-banner>
      <s-section heading={`Store Inventory (${products.length} products • ${flaggedCount} listed for rescue)`}>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "14px" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid #e1e3e5" }}>
                <th style={{ padding: "12px 8px" }}>Product</th>
                <th style={{ padding: "12px 8px" }}>Available Stock</th>
                <th style={{ padding: "12px 8px" }}>Rescue Status</th>
                <th style={{ padding: "12px 8px" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => {
                const isFlagged = product.tags.includes("near-expiry-rescue") || product.rescueStatus?.value === "LISTED_FOR_PICKUP";
                return (
                  <tr key={product.id} style={{ borderBottom: "1px solid #f1f2f3" }}>
                    <td style={{ padding: "12px 8px", fontWeight: 600 }}>{product.title}</td>
                    <td style={{ padding: "12px 8px" }}>{product.totalInventory}</td>
                    <td style={{ padding: "12px 8px" }}>
                      <span style={{ padding: "3px 10px", borderRadius: "12px", fontSize: "12px", fontWeight: 600, backgroundColor: isFlagged ? "#ffea8a" : "#aee9d1", color: isFlagged ? "#594400" : "#004c3f" }}>
                        {isFlagged ? "Listed for Pickup" : "Standard Shelf"}
                      </span>
                    </td>
                    <td style={{ padding: "12px 8px" }}>
                      <s-button variant={isFlagged ? "secondary" : "primary"} disabled={isSubmitting} onClick={() => submit({ productId: product.id, intent: isFlagged ? "clear_rescue" : "flag_rescue" }, { method: "post" })}>
                        {isFlagged ? "Remove Rescue Flag" : "Flag Near-Expiry (24h)"}
                      </s-button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </s-section>
    </s-page>
  );
}
