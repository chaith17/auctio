// auctions/static/auctions/js/websocket.js
function setupAuctionSocket(auctionId, userId, currentBidSelector) {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws/auction/${auctionId}/`);
  ws.onopen = () => console.log('ws open');
  ws.onmessage = ev => {
    const data = JSON.parse(ev.data);
    if (data.amount) {
      document.querySelector(currentBidSelector).innerText = '₹' + data.amount;
    }
  };
  document.getElementById('place-bid')?.addEventListener('click', () => {
    const amt = document.getElementById('bid-amount').value;
    if (!amt || !userId) {
      alert('Enter amount and ensure you are logged in.');
      return;
    }
    ws.send(JSON.stringify({action: 'place_bid', amount: amt, user_id: userId}));
  });
}
