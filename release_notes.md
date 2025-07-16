<h1 id="release-notes">Release Notes</h1>
<h2 id="highlights">Highlights</h2>
<ul>
<li>Enabled default telemetry collection, enhancing diagnostics and monitoring capabilities.</li>
<li>Introduced support for arbitrary variant images and multi-kernel support in the Image Customizer.</li>
<li>Significant improvements in the boot loader and error handling processes for COSI 1.1.</li>
</ul>
<h2 id="features">Features</h2>
<ul>
<li><strong>Image Customizer Enhancements</strong></li>
<li>Enable overwriting files during LiveOS reconstruction.</li>
<li>Support arbitrary variant image and multi-kernel integration for ISO/PXE flows.</li>
<li>
<p>Added PackageSnapshotTime feature with corresponding configurations.</p>
</li>
<li>
<p><strong>Telemetry &amp; Monitoring</strong></p>
</li>
<li>Default telemetry collection is now enabled.</li>
<li>Introduced telemetry error logging for Image Customizer.</li>
<li>
<p>Python telemetry hopper now supports Azure Monitor.</p>
</li>
<li>
<p><strong>COSI Support</strong></p>
</li>
<li>Enhanced bootloader metadata support for COSI 1.1.</li>
<li>Added <code>osPackages</code> field in metadata for COSI 1.1.</li>
</ul>
<h2 id="bug-fixes">Bug Fixes</h2>
<ul>
<li>Fixed backward compatibility for <code>run.sh</code> in single-arch releases.</li>
<li>Resolved build issues and refined legacy boot test handling.</li>
<li>Corrected permissions for SSH <code>authorized_keys</code> and improved UID/GID handling for initrd images.</li>
<li>Fixed a crash in the PXE build flow and ensured stability in kernel arg extraction.</li>
</ul>
<h2 id="improvements">Improvements</h2>
<ul>
<li><strong>Build and Testing</strong></li>
<li>Added functional tests to CI/CD workflows, supporting baremetal images and enhanced boot scenarios.</li>
<li>
<p>Enhanced Verity and re-init logic to prevent conflicts.</p>
</li>
<li>
<p><strong>Documentation and Usability</strong></p>
</li>
<li>Clarified documentation for user primary group configuration.</li>
<li>
<p>Updated and clarified guidance on handling COSI changes and dependencies.</p>
</li>
<li>
<p><strong>Refactoring and Code Quality</strong></p>
</li>
<li>Refactored OSModifier boot customization to support both GRUB and UKI.</li>
<li>Suppressed CodeQL warnings for improved code quality checks.</li>
</ul>
<h2 id="miscellaneous">Miscellaneous</h2>
<ul>
<li>Enabled copilot experiments for AI-driven code reviews.</li>
<li>Updated dependencies such as <code>gonum</code> to the latest versions.</li>
<li>Bumped project version to v0.16.</li>
</ul>
<p>Please refer to the detailed commit history for additional context behind each change.</p>
<p>🙌 <strong>Thanks to our top contributors:</strong> @Chris Gunn, @George Mileka, @Lanze Liu</p>