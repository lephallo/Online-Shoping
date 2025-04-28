$(document).ready(function () {
    $('.add-to-cart-btn').click(function (e) {
        e.preventDefault();
        const button = $(this);
        const productId = button.data('product-id');

        $.ajax({
            url: window.cartConfig.addToCartUrl,
            method: 'POST',
            data: {
                product_id: productId,
                quantity: 1,
                csrfmiddlewaretoken: window.cartConfig.csrfToken
            },
            success: function (response) {
                // handle success
            },
            error: function () {
                alert("Something went wrong.");
            }
        });
    });
});
