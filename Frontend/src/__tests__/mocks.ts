// utility file used by tests; keep at least one no-op test to satisfy Jest
describe('mocks bootstrap', () => {
  it('bootstraps DOM root', () => {
    const existing = document.getElementById('root');
    if (!existing) {
      const div = document.createElement('div');
      div.id = 'root';
      document.body.appendChild(div);
    }
    expect(document.getElementById('root')).toBeTruthy();
  });
});

