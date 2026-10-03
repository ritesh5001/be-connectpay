"""Builds the WordPress deliverables from index.html:

1. elementor/be-connect-home.html  - paste into an Elementor HTML widget (needs the
   "unfiltered_html" permission, otherwise WordPress strips the <style>/<script> tags).
2. wordpress-plugin/be-connect-home.zip - plugin with the [bcpay_home] shortcode.
   Works for every admin because the CSS/JS are loaded as files, not pasted.


The output is the whole homepage as one block for an Elementor "HTML" widget:
fonts + <style> + markup + <script>, with image paths pointed at IMG_BASE.
Everything in index.html is already prefixed "bcpay-" and scoped to .bcpay-home,
so no class rewriting is needed here.

Run after editing index.html:  python3 tools/build_elementor.py
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG_BASE = 'https://cdn.jsdelivr.net/gh/ritesh5001/be-connectpay@main/assets/'

page = (ROOT / 'index.html').read_text()
head = page.split('<!--BCPAY:START-->', 1)[1].split('<!--BCPAY:HEAD-END-->', 1)[0].strip()
body = page.split('<!--BCPAY:BODY-START-->', 1)[1].split('<!--BCPAY:BODY-END-->', 1)[0].strip()
code = (head + '\n' + body).replace('src="assets/', 'src="' + IMG_BASE)

out = f"""<!-- ==========================================================================
  Be-Connect Pay homepage for Elementor
  1. Page settings > Page Layout: "Elementor Canvas" (this code has its own
     header and footer). Or keep your theme layout and delete the TOP BAR,
     HEADER, Mobile menu and FOOTER blocks below.
  2. Add ONE section/container set to Full Width with 0 padding and 0 gap,
     drop in an "HTML" widget and paste everything in this file.
  All classes and ids start with "bcpay-" and every CSS rule is scoped to
  .bcpay-home, so nothing here affects other pages or widgets.
  Images load from: {IMG_BASE}
  To host them in WordPress, upload /assets to the Media Library and
  find/replace that address with your uploads folder URL.
=========================================================================== -->
{code}
"""
dest = ROOT / 'elementor' / 'be-connect-home.html'
dest.parent.mkdir(exist_ok=True)
dest.write_text(out)

# sanity checks: every rule scoped, every #ref resolvable, every image present
css = re.search(r'<style>(.*?)</style>', out, re.S).group(1)
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
sels = [s.strip() for s in re.findall(r'(?:^|[{}])\s*([^{}@]+?)\s*\{', css)]
bad = [s for s in sels if not all(p.strip().startswith(('.bcpay-home', 'body.admin-bar .bcpay-home')) or re.fullmatch(r'[\d.%\s,]+|from|to', p.strip()) for p in s.split(','))]
assert not bad, bad[:5]
ids = set(re.findall(r'\sid="([^"]+)"', out))
refs = set(re.findall(r'href="#([^"]+)"', out)) | {'bcpay-' + x for x in re.findall(r"\$\('([\w-]+)'\)", out)}
assert refs <= ids, sorted(refs - ids)
assert all(i.startswith('bcpay-') for i in ids), [i for i in ids if not i.startswith('bcpay-')]
classes = {c for v in re.findall(r'\sclass="([^"]+)"', out) for c in v.split()}
assert all(c.startswith('bcpay-') for c in classes), sorted(c for c in classes if not c.startswith('bcpay-'))
imgs = set(re.findall(re.escape(IMG_BASE) + r'([\w.-]+)', out))
missing = [i for i in imgs if not (ROOT / 'assets' / i).exists()]
assert not missing, missing
print(f'wrote {dest.relative_to(ROOT)}: {len(out):,} bytes, {len(classes)} classes, {len(ids)} ids, {len(imgs)} images')


# ---------------- WordPress plugin ----------------
import shutil, zipfile
VERSION = '1.1.0'
PLUG = ROOT / 'wordpress-plugin' / 'be-connect-home'
if PLUG.exists():
    shutil.rmtree(PLUG)
(PLUG / 'assets').mkdir(parents=True)
(PLUG / 'templates').mkdir()
shutil.copytree(ROOT / 'assets', PLUG / 'assets' / 'img')

fonts = re.search(r'<link rel="stylesheet" href="(https://fonts[^"]+)"', head).group(1)
style = re.search(r'<style>(.*?)</style>', head, re.S).group(1).strip()
(PLUG / 'assets' / 'bcpay-home.css').write_text(style + '\n')
script = re.search(r'<script>(.*?)</script>', body, re.S).group(1).strip()
(PLUG / 'assets' / 'bcpay-home.js').write_text(script + '\n')
markup = re.sub(r'<script>.*?</script>', '', body, flags=re.S).strip()
markup = markup.replace('src="assets/', 'src="{{BCPAY_IMG}}')
# no line breaks between tags, so wpautop can never add <p>/<br> into the markup
markup = re.sub(r'>\s*\n\s*<', '><', markup)
assert '\n\n' not in markup
(PLUG / 'templates' / 'home.html').write_text(markup + '\n')

php = r"""<?php
/**
 * Plugin Name:       Be-Connect Pay Homepage
 * Description:       Adds the [bcpay_home] shortcode, which displays the Be-Connect Pay homepage (banner slider, about us, calculators, services, why choose us, industries, testimonials, blog). Put it in an Elementor "Shortcode" widget.
 * Version:           __VERSION__
 * Requires at least: 5.8
 * Requires PHP:      7.2
 * Author:            Be-Connect Pay
 * License:           GPL-2.0-or-later
 * Text Domain:       bcpay-home
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'BCPAY_HOME_VERSION', '__VERSION__' );
define( 'BCPAY_HOME_FONTS', '__FONTS__' );

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
""".replace('__VERSION__', VERSION).replace('__FONTS__', fonts)
(PLUG / 'be-connect-home.php').write_text(php)

(PLUG / 'readme.txt').write_text("""=== Be-Connect Pay Homepage ===
Stable tag: """ + VERSION + """

Adds the [bcpay_home] shortcode for the Be-Connect Pay homepage.

== Installation ==
1. Plugins > Add New > Upload Plugin > choose be-connect-home.zip > Install > Activate.
2. Edit the home page with Elementor, add a "Shortcode" widget and enter: [bcpay_home]
   (Page Settings > Page Layout > "Elementor Canvas" if you use the plugin's own header and footer.)

Options:
[bcpay_home header="no"]              use your theme header instead of the plugin's
[bcpay_home footer="no"]              use your theme footer instead of the plugin's
[bcpay_home header="no" footer="no"]  homepage sections only

Every class and id starts with "bcpay-" and all CSS is scoped to .bcpay-home,
so nothing affects the rest of the site.
""")

zpath = ROOT / 'wordpress-plugin' / 'be-connect-home.zip'
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(PLUG.rglob('*')):
        if f.is_file():
            z.write(f, f.relative_to(PLUG.parent))
print(f'wrote {zpath.relative_to(ROOT)}: {zpath.stat().st_size:,} bytes')
