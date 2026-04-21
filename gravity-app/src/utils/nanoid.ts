/**
 * Tiny nanoid replacement — generates a short unique ID.
 * No dependency needed for this simple use case.
 */
export function nanoid(size = 8): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  const arr = new Uint8Array(size)
  crypto.getRandomValues(arr)
  arr.forEach((byte) => (result += chars[byte % chars.length]))
  return result
}
