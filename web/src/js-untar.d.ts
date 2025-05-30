declare module "js-untar" {
  export function untar(buffer: ArrayBuffer): Promise<any[]>;
}