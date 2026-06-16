# JSON_Escape: Return string with all special characters escaped
# ©2015 Red Lion Controls, Inc. All rights reserved. Red Lion, the Red Lion logo and Sixnet are registered trademarks of Red Lion Controls, Inc. All other company and product names are trademarks of their respective owners.
sub JSON_Escape {
	my $__value = $_[0];
	$__value =~ s/\\/\\\\/g;
	$__value =~ s/"/\\"/g;
	$__value =~ s/\n/\\n/g;
	$__value =~ s/\t/\\t/g;
	$__value =~ s/\r/\\r/g;
	return $__value;
}

# JSON_Quote: Return string wrapped in quotes if necessary
#     Boolean strings (true/false), null, and floating point numbers do not
#     need to be quoted, and will simply be returned
sub JSON_Quote {
	my $__value = shift;

	if ($__value =~ /^(-?([1-9]\d*|0)(\.\d+)?|true|false|null)$/) {
		return $__value;
	}
	return "\"$__value\"";
}

# JSON_Serialize: Return a string/serialized version of a perl object
sub JSON_Serialize {
	my $__obj = shift;
	my $__jstr = "";

	if (! ref($__obj)) {
		$__jstr = &JSON_Quote(&JSON_Escape($__obj));
	}
	elsif (ref($__obj) eq "SCALAR") {
		$__jstr = &JSON_Quote(&JSON_Escape(${$__obj}));
	}
	elsif (ref($__obj) eq "ARRAY") {
		my @arr = @{$__obj};
		$__jstr .= "[";
		for (my $i=0; $i<=$#arr; $i++) {
			if ($i > 0) {
				$__jstr .= ",";
			}
			$__jstr .= &JSON_Serialize($arr[$i]);
		}
		$__jstr .= "]";
	}
	elsif (ref($__obj) eq "HASH") {
		my %__hash = %{$__obj};
		my $__comma = 0;
		$__jstr .= "{";
		keys %__hash;
		while (my ($k, $v) = each %__hash) {
			if ($__comma) {
				$__jstr .= ",";
			}
			else {
				$__comma = 1;
			}
			$__jstr .= "\"" . &JSON_Escape($k) . "\":" . &JSON_Serialize($v);
		}
		$__jstr .= "}";
	}
	else {
		return "\"Unknown\"";
	}
	return $__jstr;
}

1; # return true
