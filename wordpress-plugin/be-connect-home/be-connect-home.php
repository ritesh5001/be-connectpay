<?php
/**
 * Plugin Name:       Be-Connect Pay Homepage
 * Description:       Adds the [bcpay_home] shortcode, which displays the Be-Connect Pay homepage (banner slider, about us, calculators, services, why choose us, industries, testimonials, blog). Put it in an Elementor "Shortcode" widget.
 * Version:           1.1.0
 * Requires at least: 5.8
 * Requires PHP:      7.2
 * Author:            Be-Connect Pay
 * License:           GPL-2.0-or-later
 * Text Domain:       bcpay-home
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'BCPAY_HOME_VERSION', '1.1.0' );
define( 'BCPAY_HOME_FONTS', 'https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap' );

/**
 * Registers the stylesheet and script.
 */
function bcpay_home_register_assets() {
	$url = plugin_dir_url( __FILE__ ) . 'assets/';
	wp_register_style( 'bcpay-home-fonts', BCPAY_HOME_FONTS, array(), null );
	wp_register_style( 'bcpay-home', $url . 'bcpay-home.css', array( 'bcpay-home-fonts' ), BCPAY_HOME_VERSION );
	wp_register_script( 'bcpay-home', $url . 'bcpay-home.js', array(), BCPAY_HOME_VERSION, true );
}
add_action( 'wp_enqueue_scripts', 'bcpay_home_register_assets', 5 );

/**
 * Loads the CSS in <head> on pages that use the shortcode (classic content or
 * Elementor data), so the page never flashes unstyled.
 */
function bcpay_home_enqueue_on_shortcode_pages() {
	if ( ! is_singular() ) {
		return;
	}
	$id      = get_queried_object_id();
	$content = (string) get_post_field( 'post_content', $id ) . (string) get_post_meta( $id, '_elementor_data', true );
	if ( false !== strpos( $content, 'bcpay_home' ) ) {
		wp_enqueue_style( 'bcpay-home' );
	}
}
add_action( 'wp_enqueue_scripts', 'bcpay_home_enqueue_on_shortcode_pages', 20 );

/**
 * [bcpay_home header="yes" footer="yes"]
 *
 * header="no" hides the plugin's top bar, header and mobile menu (use your theme's header).
 * footer="no" hides the plugin's footer (use your theme's footer).
 *
 * @param array|string $atts Shortcode attributes.
 * @return string
 */
function bcpay_home_shortcode( $atts ) {
	$atts = shortcode_atts(
		array(
			'header' => 'yes',
			'footer' => 'yes',
		),
		$atts,
		'bcpay_home'
	);

	$file = plugin_dir_path( __FILE__ ) . 'templates/home.html';
	if ( ! is_readable( $file ) ) {
		return '';
	}
	$html = (string) file_get_contents( $file ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
	$html = str_replace( '{{BCPAY_IMG}}', esc_url( plugin_dir_url( __FILE__ ) . 'assets/img/' ), $html );

	if ( in_array( strtolower( (string) $atts['header'] ), array( 'no', 'false', '0', 'off' ), true ) ) {
		$html = preg_replace( '/<!--BCPAY:HEADER-START-->.*?<!--BCPAY:HEADER-END-->/s', '', $html );
	}
	if ( in_array( strtolower( (string) $atts['footer'] ), array( 'no', 'false', '0', 'off' ), true ) ) {
		$html = preg_replace( '/<!--BCPAY:FOOTER-START-->.*?<!--BCPAY:FOOTER-END-->/s', '', $html );
	}

	$assets = plugin_dir_url( __FILE__ ) . 'assets/';
	$out    = '';

	// CSS not queued for <head> (e.g. shortcode used in a template or header): load it here instead.
	if ( ! wp_style_is( 'bcpay-home', 'enqueued' ) && ! wp_style_is( 'bcpay-home', 'done' ) ) {
		$out .= '<link rel="stylesheet" href="' . esc_url( BCPAY_HOME_FONTS ) . '">';
		$out .= '<link rel="stylesheet" href="' . esc_url( $assets . 'bcpay-home.css?ver=' . BCPAY_HOME_VERSION ) . '">';
	}

	$out .= $html;

	// Elementor's editor re-renders widgets over AJAX, so the script has to come with the markup there.
	$is_editor = wp_doing_ajax() || isset( $_GET['elementor-preview'] ); // phpcs:ignore WordPress.Security.NonceVerification.Recommended
	if ( $is_editor ) {
		$out .= '<script src="' . esc_url( $assets . 'bcpay-home.js?ver=' . BCPAY_HOME_VERSION ) . '"></script>'; // phpcs:ignore WordPress.WP.EnqueuedResources.NonEnqueuedScript
	} else {
		wp_enqueue_script( 'bcpay-home' );
	}

	return $out;
}
add_shortcode( 'bcpay_home', 'bcpay_home_shortcode' );
