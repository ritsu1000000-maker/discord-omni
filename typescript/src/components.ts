export const COMPONENTS_V2_FLAG = 1 << 15;

export function textDisplay(content: string) {
  return { type: 10, content };
}

export function button(label: string, customId: string, style = 1) {
  return { type: 2, label, custom_id: customId, style };
}

export function actionRow(...components: unknown[]) {
  return { type: 1, components };
}

export function container(...components: unknown[]) {
  return { type: 17, components };
}
