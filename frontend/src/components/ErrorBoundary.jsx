import { Component } from "react";

// Si una página truena, mostramos un aviso en vez de dejar la pantalla en blanco.
export default class ErrorBoundary extends Component {
  state = { error: null };
  static getDerivedStateFromError(error) {
    return { error };
  }
  componentDidUpdate(prev) {
    if (prev.resetKey !== this.props.resetKey && this.state.error) this.setState({ error: null });
  }
  render() {
    if (!this.state.error) return this.props.children;
    return (
      <main className="rg-app rg-app--phone">
        <div className="rg-phone">
          <p className="rg-eyebrow">Algo salió mal</p>
          <h1>No pudimos mostrar esta sección</h1>
          <p className="rg-muted">{String(this.state.error.message || this.state.error)}</p>
          <a className="rg-pill rg-pill--blue" href="#/">Volver al inicio</a>
        </div>
      </main>
    );
  }
}
