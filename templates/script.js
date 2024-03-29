document.addEventListener("DOMContentLoaded", function() {
    const addToCartButtons = document.querySelectorAll(".add-to-cart");
    const cartCount = document.getElementById("cart-count");

    let cartItems = 0;

    addToCartButtons.forEach(button => {
        button.addEventListener("click", function() {
            cartItems++;
            cartCount.textContent = cartItems;
        });
    });
});
