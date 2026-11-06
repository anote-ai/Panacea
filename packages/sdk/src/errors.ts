/** An API call failed: `status` is the HTTP status and `body` the parsed error. */
export class AnoteError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body: unknown,
  ) {
    super(message);
    this.name = "AnoteError";
  }
}
